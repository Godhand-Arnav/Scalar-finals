"""Episode creation and state routes (OpenEnv spec)."""

from __future__ import annotations
import random
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException

from env.misinfo_env import MisInfoForensicsEnv
from server.schemas import ResetRequest, ResetResponse, StateRequest, StateResponse
from server.state import EPISODE_STORE

router = APIRouter()


@router.post("/reset", response_model=ResetResponse, status_code=200)
async def reset_env(req: ResetRequest):
    try:
        task_names = [req.task_name] if req.task_name else None
        env = MisInfoForensicsEnv(
            task_names=task_names,
            difficulty=req.difficulty,
            use_live_tools=req.use_live_tools,
        )
        seed = req.seed or random.randint(0, 2**31)
        obs, info = env.reset(seed=seed)

        episode_id = info["episode_id"]
        EPISODE_STORE[episode_id] = {
            "env":      env,
            "obs":      obs,
            "agent_id": req.agent_id or "anonymous",
            "total_reward": 0.0,
            "verdict":  None,
            "done":     False,
        }
        
        # In strict single-tenant, we cache the most recent
        EPISODE_STORE["latest"] = EPISODE_STORE[episode_id]

        return ResetResponse(
            episode_id=episode_id,
            observation=obs.tolist(),
            info=info,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/state", response_model=StateResponse)
async def get_state(episode_id: Optional[str] = None):
    eid = episode_id or "latest"
    if eid not in EPISODE_STORE:
        raise HTTPException(status_code=404, detail="Active episode not found")
    
    record = EPISODE_STORE[eid]
    env = record["env"]
    info = env.get_episode_summary()
    if env.graph:
        info["graph_summary"] = env.graph.to_dict()

    return StateResponse(
        episode_id=eid,
        observation=record["obs"].tolist(),
        done=record["done"],
        total_reward=record["total_reward"],
        info=info,
    )
