"""Step execution routes (OpenEnv spec)."""

from __future__ import annotations
import logging
from fastapi import APIRouter, HTTPException
from server.schemas import StepRequest, StepResponse
from server.state import EPISODE_STORE

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/step", response_model=StepResponse)
async def take_step(req: StepRequest):
    eid = req.episode_id or EPISODE_STORE.get("latest_id")
    if not eid or eid not in EPISODE_STORE:
        raise HTTPException(status_code=404, detail="Active episode not found")

    record = EPISODE_STORE[eid]
    if record["done"]:
        raise HTTPException(status_code=400, detail="Episode is already done. Call /reset")

    env = record["env"]
    try:
        obs, reward, terminated, truncated, info = env.step(req.action)
    except AssertionError as e:
        # AssertionError text comes exclusively from our own env code, so it
        # is safe to surface as a 400 detail (no user-controlled content).
        logger.warning("step assertion (episode=%s): %s", eid, e)
        raise HTTPException(status_code=400, detail=str(e))

    done = terminated or truncated
    record["obs"] = obs
    record["total_reward"] += reward
    record["done"] = done

    if info.get("verdict"):
        record["verdict"] = info["verdict"]

    # Append to episode trace for task grader
    from env.misinfo_env import ACTIONS
    record.setdefault("episode_trace", []).append({
        "step": env.steps,
        "action": ACTIONS[req.action],
        "reward": reward,
        "done": done,
    })

    return StepResponse(
        observation=obs.tolist(),
        reward=round(float(reward), 5),
        done=done,
        info=info,
    )
