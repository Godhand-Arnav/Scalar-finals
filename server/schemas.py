"""
server/schemas.py — OpenEnv Compatible API schemas
"""

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class ResetRequest(BaseModel):
    task_name: Optional[str] = None
    difficulty: int = 1
    seed: Optional[int] = None
    use_live_tools: bool = False
    agent_id: Optional[str] = None


class ResetResponse(BaseModel):
    episode_id: str
    observation: List[float]
    info: Dict[str, Any]


class StepRequest(BaseModel):
    episode_id: Optional[str] = None  # Optional for single-tenant mode
    action: int = Field(..., ge=0, le=12)


class StepResponse(BaseModel):
    observation: List[float]
    reward: float
    done: bool
    info: Dict[str, Any]


class StateRequest(BaseModel):
    episode_id: Optional[str] = None


class StateResponse(BaseModel):
    episode_id: str
    observation: List[float]
    done: bool
    total_reward: float
    info: Dict[str, Any]
