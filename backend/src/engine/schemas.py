from typing import List, Optional
from pydantic import BaseModel, Field


class ResolverOutput(BaseModel):
    action: Optional[str] = Field(
        None, description="allow, deny, block, permit; null if unclear"
    )

    sources: List[str] = Field(
        default_factory=list,
        description="Source entities mentioned in the policy (raw or context-mapped)"
    )

    destinations: List[str] = Field(
        default_factory=list,
        description="Destination entities or domains mentioned in the policy"
    )

    protocols: List[str] = Field(
        default_factory=list,
        description="tcp, udp, icmp, any; inferred or raw"
    )

    ports: List[int] = Field(
        default_factory=list,
        description="Explicitly stated or inferred port numbers"
    )

    service_names: List[str] = Field(
        default_factory=list,
        description="Service names like HTTPS, SSH, DNS"
    )

    direction: Optional[str] = Field(
        None, description="inbound, outbound, any; null if not specified"
    )

    schedule: Optional[str] = Field(
        None, description="Time window mentioned; null if missing"
    )

    logging: Optional[bool] = Field(
        None, description="Whether logging was mentioned"
    )

    ambiguities: List[str] = Field(
        default_factory=list,
        description="List of unresolved or vague parts"
    )

    raw_policy: str = Field(
        ..., description="Exact user input"
    )

    class Config:
        extra = "forbid"


class IRRule(BaseModel):
    id: str = Field(..., description="Unique rule identifier, e.g., r1, r2.")
    action: str = Field(..., description="allow or deny")

    src: List[str] = Field(
        ..., description="Source object names"
    )
    dst: List[str] = Field(
        ..., description="Destination object names"
    )

    protocol: str = Field(..., description="tcp, udp, icmp, or any")
    dst_ports: List[int] = Field(
        ..., description="Destination port numbers"
    )

    src_zone: str = Field(..., description="Zone of the source object")
    dst_zone: str = Field(..., description="Zone of the destination object")

    direction: Optional[str] = Field(
        None, description="inbound, outbound, any, or null"
    )

    schedule: Optional[str] = Field(
        None, description="Schedule name or null"
    )

    log: bool = Field(..., description="Whether logging is enabled")
    priority: int = Field(..., description="100 for allow, 10 for deny")

    class Config:
        extra = "forbid"



class IRMetadata(BaseModel):
    raw_policy: str
    warnings: List[str]
    context_used: bool

    class Config:
        extra = "forbid"


class IRBuilderOutput(BaseModel):
    rules: List[IRRule]
    metadata: IRMetadata

    class Config:
        extra = "forbid"
