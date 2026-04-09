import asyncio
import json
from typing import List, Optional

# Import our environment and tasks
from legal_env import LegalRedLineEnv, LegalAction
from tasks import TASKS

import json

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action, reward: float, done: bool = False, error: str = None) -> None:
    if isinstance(action, dict):
        out = action.copy()
        out["reward"] = round(reward, 2)
        out["done"] = done
        out["error"] = error
        print(json.dumps(out, indent=2), flush=True)
    elif action == "ERROR":
        out = {
            "simplified_text": "ERROR",
            "risk": "UNKNOWN",
            "key_points": [],
            "reward": max(0.01, round(reward, 2)),
            "done": done,
            "error": error
        }
        print(json.dumps(out, indent=2), flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"\n[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}", flush=True)

async def run_mock_task(task_index: int):
    # Initialize environment
    env = LegalRedLineEnv(task_index=task_index)
    task_data = TASKS[task_index]
    
    # Sync reset
    obs = env.reset()
    log_start(task=obs.task_name, env="legal_red_line", model="mock-model")
    
    # Generate a "Perfect" action based on the task data
    # We use some words from keywords to ensure 1.0 score
    mock_simplified = " ".join(task_data.simplified_text_keywords)
    mock_points = task_data.key_points_keywords
    
    mock_action = LegalAction(
        simplified_text=f"Simplified version covering {mock_simplified}",
        risk=task_data.risk,
        key_points=mock_points
    )
    
    # Execute the step
    obs = env.step(mock_action)
    
    # Log the result
    action_dict = mock_action.model_dump()
    log_step(step=1, action=action_dict, reward=obs.reward, done=obs.done)
    
    log_end(success=True, steps=1, score=obs.reward, rewards=[obs.reward])
    env.close()

async def main():
    print("--- RUNNING MOCK INFERENCE (NO API KEY REQUIRED) ---", flush=True)
    for i in range(len(TASKS)):
        await run_mock_task(i)
        print("-" * 40, flush=True)

if __name__ == "__main__":
    asyncio.run(main())
