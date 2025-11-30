import unittest
import json
import os
import sys
import argparse
import difflib
import datetime
from dotenv import load_dotenv

# Load .env file from backend directory explicitly
env_path = os.path.join(os.path.dirname(__file__), '../.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

# Handle command line arguments for live tests
ENABLE_LIVE_TESTS = False
if '--live' in sys.argv:
    ENABLE_LIVE_TESTS = True
    sys.argv.remove('--live')  # Remove it so unittest.main doesn't complain

# If running in mocked mode (not live), provide a dummy key ONLY if real one is missing
# This prevents crashes during import if .env is missing or empty
if not ENABLE_LIVE_TESTS and "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = "sk-dummy-key-for-testing"

# Add backend root to path so we can import src as a package
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.engine.compiler.palo_alto import PaloAltoCompiler
from src.engine.schemas import IRBuilderOutput
from src.engine import agents

class TestPipelineTriplets(unittest.TestCase):
    # ANSI Color Codes
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    RESET = '\033[0m'

    def setUp(self):
        self.compiler = PaloAltoCompiler()
        self.tests_dir = os.path.join(os.path.dirname(__file__), '../../data/tests/')
        self.samples_path = os.path.join(os.path.dirname(__file__), '../../data/samples')
        
        # Load all *_tests.json files
        self.all_triplets = []
        for filename in os.listdir(self.tests_dir):
            if filename.endswith('_tests.json'):
                with open(os.path.join(self.tests_dir, filename), 'r') as f:
                    self.all_triplets.extend(json.load(f))

    def test_triplets(self):
        """
        Main test dispatcher.
        Runs EITHER in Mocked mode (default) OR Live mode (if --live flag was present).
        """
        if ENABLE_LIVE_TESTS:
            self._run_live_tests()
        else:
            self._run_mocked_tests()

    def _run_mocked_tests(self):
        print(f"\nRunning {len(self.all_triplets)} mocked triplet tests...")

        for case in self.all_triplets:
            with self.subTest(case_id=case['id']):
                print(f"\nTesting case: {case['id']} - {case['description']}")

                # 1. Load Expected IR directly from JSON
                # We skip calling agents entirely since we just want to verify the compiler logic
                ir_out = IRBuilderOutput.model_validate(case['expected_ir'])

                # 2. Run Compiler
                cli_output = self.compiler.compile_policy(ir_out)

                # 3. Verify CLI matches expectation
                self.assertEqual(cli_output.strip(), case['expected_cli'].strip())
                
                print(f"  {self.GREEN}[PASS]{self.RESET} {case['id']}")

    def _run_live_tests(self):
        # Setup log file
        timestamp = datetime.datetime.now().strftime("%d-%m-%y_%H-%M")
        log_filename = f"{timestamp}_test_log.txt"
        log_path = os.path.join(os.path.dirname(__file__), 'output', log_filename)
        
        # Ensure output dir exists (safety check, though mkdir was run)
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        print(f"\nRunning {len(self.all_triplets)} LIVE triplet tests...")
        print(f"Logging output to: {log_path}")
        
        # CLI Similarity Threshold (strict 100% for firewall rules)
        SIMILARITY_THRESHOLD = 100.0
        
        passed_tests = []
        failed_tests = []
        
        with open(log_path, 'w') as log_file:
            log_file.write(f"Test Run: {timestamp}\n")
            log_file.write("="*50 + "\n\n")

            for case in self.all_triplets:
                with self.subTest(case_id=case['id']):
                    print("\n+", "-"*50, "+", sep="")
                    print(f"LIVE Testing case: {case['id']}")
                    
                    log_file.write(f"TEST CASE: {case['id']}\n")
                    log_file.write("-" * 30 + "\n")
                    
                    ctx_path = os.path.join(self.samples_path, case['context_file'])
                    with open(ctx_path, 'r') as f:
                        context = json.load(f)

                    # Call real agents
                    try:
                        resolver_out = agents.resolve_policy(case['nl_query'], context)
                        ir_out = agents.build_ir(resolver_out, context)
                    except Exception as e:
                        print(f"  {self.RED}[ERROR]{self.RESET} Agent execution failed: {e}")
                        log_file.write(f"STATUS: ERROR\nReason: {str(e)}\n\n")
                        failed_tests.append(case['id'])
                        continue
                    
                    # Compare IR
                    generated_ir_dict = ir_out.model_dump()
                    if generated_ir_dict != case['expected_ir']:
                         print(f"  {self.YELLOW}[WARN]{self.RESET} Generated IR differs from Expected for {case['id']}")
                         log_file.write("WARNING: IR Mismatch\n")
                         # print(f"Expected:\n{case['expected_ir']}\nGot:\n{generated_ir_dict}")

                    # Compile
                    cli_output = self.compiler.compile_policy(ir_out)
                    
                    # Verify CLI with Similarity
                    expected = case['expected_cli'].strip()
                    actual = cli_output.strip()
                    
                    similarity = difflib.SequenceMatcher(None, expected, actual).ratio() * 100
                    
                    print()
                    if similarity < SIMILARITY_THRESHOLD:
                        print(f"  {self.RED}[FAIL]{self.RESET} CLI Similarity: {similarity:.2f}% (Threshold: {SIMILARITY_THRESHOLD}%)")
                        print(f"Expected:\n{expected}\nGot:\n{actual}")
                        
                        log_file.write(f"STATUS: FAIL (Similarity: {similarity:.2f}%)\n")
                        log_file.write("EXPECTED CLI:\n")
                        log_file.write(expected + "\n")
                        log_file.write("ACTUAL CLI:\n")
                        log_file.write(actual + "\n\n")
                        
                        failed_tests.append(case['id'])
                    else:
                        print(f"  {self.GREEN}[PASS]{self.RESET} {case['id']} - Exact CLI match (100.00%)")
                        log_file.write("STATUS: PASS\n\n")
                        passed_tests.append(case['id'])
            
            # Summary Report
            print("\n" + "="*50)
            print("LIVE TEST SUMMARY")
            print("="*50)
            print(f"Total Tests: {len(self.all_triplets)}")
            print(f"Passed:      {len(passed_tests)}")
            print(f"Failed:      {len(failed_tests)}")
            
            log_file.write("="*50 + "\n")
            log_file.write("SUMMARY\n")
            log_file.write("="*50 + "\n")
            log_file.write(f"Total: {len(self.all_triplets)}\n")
            log_file.write(f"Passed: {len(passed_tests)}\n")
            log_file.write(f"Failed: {len(failed_tests)}\n")

            if failed_tests:
                print("\nFailed Cases:")
                log_file.write("\nFAILED CASES:\n")
                for case_id in failed_tests:
                    print(f"- {self.RED}{case_id}{self.RESET}")
                    log_file.write(f"- {case_id}\n")
            print("="*50 + "\n")
        
if __name__ == '__main__':
    unittest.main()

