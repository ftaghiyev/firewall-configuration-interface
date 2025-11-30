import os
import tempfile
import logging
import uuid
import concurrent.futures
from typing import List, Optional

try:
    from pybatfish.client.session import Session
    HAS_BATFISH = True
except ImportError:
    HAS_BATFISH = False

logger = logging.getLogger(__name__)

# Timeout in seconds for Batfish operations
BATFISH_TIMEOUT = 15

class BatfishManager:
    _instance = None
    _session = None

    def __new__(cls, host: str = "localhost", port: int = 9996):
        if cls._instance is None:
            cls._instance = super(BatfishManager, cls).__new__(cls)
            cls._instance.host = host
            cls._instance.port = port
            cls._instance.enabled = HAS_BATFISH
            cls._instance._session = None
        return cls._instance

    def get_session(self):
        """
        Get or create a Batfish session.
        """
        if not self.enabled:
            return None

        if self._session is None:
            try:
                # Session objects are lightweight, but we want to avoid recreating them if possible
                # to maintain connection state or config if relevant.
                # However, pybatfish Sessions are mainly client wrappers.
                self._session = Session(host=self.host)
                logger.info(f"Connected to Batfish at {self.host}")
            except Exception as e:
                logger.error(f"Failed to connect to Batfish: {e}")
                return None
        return self._session

    def _fmt(self, x: str) -> str:
        """Quote names containing spaces or special chars."""
        if " " in x or "-" in x:
            return f'"{x}"'
        return x
        
    def _run_validation_logic(self, bf, temp_dir, snapshot_name) -> List[dict]:
        """
        Internal logic to run Batfish analysis. 
        This is separated to allow wrapping in a timeout.
        Returns a list of warning dicts: { "severity": "warning"|"error", "message": "..." }
        """
        warnings = []
        bf.init_snapshot(temp_dir, name=snapshot_name, overwrite=True)
        
        # 1. Check for parsing/initialization issues
        issues = bf.q.initIssues().answer().frame()
        if not issues.empty:
            for _, row in issues.iterrows():
                # Categorize specific known issues if needed, but default to warning or error based on Type
                issue_type = row.get('Type', 'Unknown')
                details = row.get('Details', '')
                msg = f"Batfish Issue: {issue_type} - {details}"
                
                if 'Line_Text' in row and row['Line_Text']:
                        msg += f" (Line: {row['Line_Text']})"
                
                # Treat syntax errors as errors, others as warnings (or redflags)
                severity = "error" if "Error" in issue_type else "warning"
                warnings.append({"severity": severity, "message": msg})

        # 2. Check for undefined references
        undef_refs = bf.q.undefinedReferences().answer().frame()
        if not undef_refs.empty:
            for _, row in undef_refs.iterrows():
                msg = f"Batfish Undefined Ref: {row.get('Struct_Type')} '{row.get('Ref_Name')}'"
                if 'Lines' in row and row['Lines']:
                        msg += f" at lines {row['Lines']}"
                # Undefined references are usually critical for correct analysis
                warnings.append({"severity": "error", "message": msg})
        
        # 3. Check for unused structures
        unused = bf.q.unusedStructures().answer().frame()
        if not unused.empty:
             for _, row in unused.iterrows():
                msg = f"Batfish Unused: {row.get('Structure_Type')} '{row.get('Structure_Name')}'"
                warnings.append({"severity": "warning", "message": msg})
        
        return warnings

    def validate(self, config_content: str, context: Optional[dict] = None, filename: str = "firewall.cfg") -> List[dict]:
        """
        Validate a configuration using Batfish.
        Returns a list of warning dicts.
        
        Args:
            config_content: The vendor-specific configuration text.
            context: Optional dictionary containing network definitions (zones, objects).
                     If provided, header configurations will be generated from this.
            filename: The name of the file to be simulated.
        """
        if not self.enabled:
            return [{"severity": "error", "message": "Batfish validation skipped: pybatfish not installed."}]

        bf = self.get_session()
        if not bf:
            return [{"severity": "error", "message": "Batfish validation skipped: Could not connect to Batfish service."}]

        # Generate header based on context if available
        header_lines = [
            "set deviceconfig system type static",
            "set deviceconfig system hostname fw-validator-01"
        ]

        # Standard default setup
        header_lines.extend([
            "set network interface ethernet ethernet1/1 layer3 ip 192.168.1.1/24",
            "set network virtual-router default interface ethernet1/1",
            "set zone trust network layer3 ethernet1/1",
            "set network interface ethernet ethernet1/2 layer3 ip 10.0.0.1/24",
            "set network virtual-router default interface ethernet1/2", 
            "set zone untrust network layer3 ethernet1/2"
        ])

        if context:
            # Check if we are dealing with a RequestContext model or a plain dict. 
            # If coming from the cached dict in policies.py, it is already a dict.
            # But standard payload structure puts the details inside "details".
            
            network_def = context.get("details", {})
            
            # Fallback: if "objects" or "zones" are at the top level (simple test cases)
            if "objects" in context or "zones" in context:
                network_def = context

            # Define zones to avoid undefined reference errors
            if "zones" in network_def:
                for i, zone_name in enumerate(network_def["zones"]):
                    # ...
                    pass

            # Define Address Objects
            if "objects" in network_def:
                for name, val in network_def["objects"].items():
                    safe_name = self._fmt(name)
                    # val could be IP string or list of IPs/FQDNs
                    # Simple heuristic:
                    if isinstance(val, str):
                        # "10.10.10.0/24" or "1.1.1.1"
                        if "/" in val:
                            # Subnet
                            header_lines.append(f"set address {safe_name} ip-netmask {val}")
                        else:
                            # Host
                            header_lines.append(f"set address {safe_name} ip-netmask {val}/32")
                    elif isinstance(val, list):
                        # Likely FQDNs or list of IPs - simpler to treat as FQDN for now or skip if complex
                        # Batfish supports FQDN addresses
                        if val:
                            header_lines.append(f"set address {safe_name} fqdn {val[0]}")

            # Define Zones explicitly as Layer3 zones
            if "zones" in network_def:
                # Let's try creating a loopback per zone.
                idx = 1
                for zone in network_def["zones"]:
                    if zone in ["trust", "untrust"]: 
                        continue # already defined
                    
                    safe_zone = self._fmt(zone)
                    idx += 1
                    if_name = f"loopback.{idx}"
                    header_lines.append(f"set network interface loopback units {if_name} ip 1.1.1.{idx}/32")
                    header_lines.append(f"set network virtual-router default interface {if_name}")
                    header_lines.append(f"set zone {safe_zone} network layer3 {if_name}")

        
        full_content = "\n".join(header_lines) + "\n\n" + config_content

        warnings = []
        
        # Use backend/tmp directory for snapshots
        base_tmp_dir = os.path.join(os.getcwd(), "backend", "tmp")
        os.makedirs(base_tmp_dir, exist_ok=True)

        # Create a unique temporary directory for this snapshot
        with tempfile.TemporaryDirectory(dir=base_tmp_dir) as temp_dir:
            configs_dir = os.path.join(temp_dir, "configs")
            os.makedirs(configs_dir)
            
            # Write the config file
            config_path = os.path.join(configs_dir, filename)
            with open(config_path, "w") as f:
                f.write(full_content)

            snapshot_name = f"snap_{uuid.uuid4().hex[:8]}"
            
            try:
                # Wrap the Batfish execution in a thread pool to enforce timeout
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(self._run_validation_logic, bf, temp_dir, snapshot_name)
                    warnings = future.result(timeout=BATFISH_TIMEOUT)
                    
            except concurrent.futures.TimeoutError:
                logger.error(f"Batfish validation timed out after {BATFISH_TIMEOUT}s")
                warnings.append({"severity": "error", "message": f"Error: Batfish validation timed out after {BATFISH_TIMEOUT}s. Please check Batfish service connectivity."})
            except Exception as e:
                logger.error(f"Batfish validation failed: {e}")
                warnings.append({"severity": "error", "message": f"Error: Batfish validation failed: {str(e)}"})

        return warnings
