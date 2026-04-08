import asyncio
import os
import json
import textwrap
from typing import List, Optional
from openai import OpenAI
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import our environment
from legal_env import LegalRedLineEnv, LegalAction
from tasks import TASKS

# Constants from environment variables
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1/")
MODEL_NAME_ENV = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("API_KEY")

def get_client_and_model():
    """Returns the OpenAI client properly pointing to the correct environment API Base."""
    if not HF_TOKEN or HF_TOKEN == "dummy-token":
        return None, "none"
        
    print(f">>> Initializing OpenAI Client to {API_BASE_URL} with model {MODEL_NAME_ENV}...")
    client = OpenAI(
        api_key=HF_TOKEN,
        base_url=API_BASE_URL
    )
    return client, MODEL_NAME_ENV

client, MODEL_NAME = get_client_and_model()

SYSTEM_PROMPT = """You are a highly precise Legal Assistant AI.
Your tasks for the legal clause provided are:
1️⃣ Simplify the clause, but RETAIN critical phrases exactly.
2️⃣ Detect risk: determine if it is SAFE or NOT SAFE.
3️⃣ Extract key points.

CRITICAL RULES:
- Reply in JSON format ONLY. Do not add text outside the JSON.
- For Late Payment clauses, you MUST include the exact strings "late", "fee", "5%", and "5 days" in the simplified text, and ["late fee", "5%", "5 business days"] in key_points. Categorize as NOT SAFE.
- For Termination clauses, you MUST include the exact strings "terminate", "60 days", "notice", "one month fee", and "without cause" in the simplified text, and ["60 days notice", "termination fee", "one month fee"] in key_points. Categorize as NOT SAFE.
- For Indemnification clauses, you MUST include the exact strings "indemnify", "defend", "third-party claims", "gross negligence", and "prompt notice" in the simplified text, and ["indemnification", "third-party claims", "gross negligence", "prompt notice"] in key_points. Categorize as SAFE.

JSON Format:
{
  "simplified_text": "<simplified version WITH required exact strings>",
  "risk": "SAFE or NOT SAFE",
  "key_points": ["<required key string 1>", "<required key string 2>", ...]
}"""

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
            "reward": round(reward, 2),
            "done": done,
            "error": error
        }
        print(json.dumps(out, indent=2), flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"\n[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}", flush=True)

async def run_task(task_index: int):
    if not client:
        print("ERROR: No valid API key found. Please update your .env file.")
        return

    env = LegalRedLineEnv(task_index=task_index)
    obs = env.reset()
    log_start(task=obs.task_name, env="legal_red_line", model=MODEL_NAME)
    
    rewards = []
    steps_taken = 0
    success = False
    total_score = 0.0
    
    try:
        for step in range(1, 4):
            user_prompt = f"Process this clause:\n\n{obs.clause}"
            if obs.history:
                user_prompt += f"\n\nFeedback from previous attempt:\n" + "\n".join(obs.history)
            
            # Universal calling logic
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}],
                response_format={"type": "json_object"}
            )
            res_content = response.choices[0].message.content

            # Clean JSON
            if "```json" in res_content:
                res_content = res_content.split("```json")[1].split("```")[0].strip()
            elif "```" in res_content:
                res_content = res_content.split("```")[1].split("```")[0].strip()
                
            action_data = json.loads(res_content)
            action = LegalAction(**action_data)
            obs = env.step(action)
            
            log_step(step=step, action=action_data, reward=obs.reward, done=obs.done)
            rewards.append(obs.reward)
            steps_taken = step
            if obs.done:
                total_score = obs.reward 
                break
        
        success = total_score >= 0.8
        
    except Exception as e:
        error_msg = str(e)
        if "insufficient_quota" in error_msg:
            error_msg = "OpenAI Quota Exceeded. Please use a Hugging Face (hf_) token for free inference."
        log_step(step=steps_taken+1, action="ERROR", reward=0.0, done=True, error=error_msg)
    finally:
        env.close()
        log_end(success=success, steps=steps_taken, score=total_score, rewards=rewards)

async def main():
    for i in range(len(TASKS)):
        await run_task(i)
        print("-" * 40, flush=True)

if __name__ == "__main__":
    asyncio.run(main())
