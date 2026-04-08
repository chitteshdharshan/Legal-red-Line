import asyncio
from legal_env import LegalRedLineEnv, LegalAction

async def main():
    print("--- RUNNING NEGATIVE TEST CASES ---", flush=True)
    
    env = LegalRedLineEnv(task_index=0) # late_payment_penalty (expected NOT SAFE)
    
    print("\n[Negative Test 1]: Wrong Risk Assessment")
    obs = env.reset()
    bad_action_1 = LegalAction(
        simplified_text="late fee 5% 5 days", # all correct keywords here
        risk="SAFE", # WRONG (should be NOT SAFE)
        key_points=["late fee", "5%", "5 business days"] # all correct keywords here
    )
    obs = env.step(bad_action_1)
    print(f"Assigned Score: {obs.reward:.2f} / 1.00")
    print(f"Grader Feedback: {obs.metadata['feedback']}")
    
    print("\n[Negative Test 2]: Missing Details in Simplified Text")
    obs = env.reset()
    bad_action_2 = LegalAction(
        simplified_text="You will be penalized if you wait too long to pay.", # Missing exact keywords
        risk="NOT SAFE", # Correct
        key_points=["late fee", "5%", "5 business days"] # Correct
    )
    obs = env.step(bad_action_2)
    print(f"Assigned Score: {obs.reward:.2f} / 1.00")
    print(f"Grader Feedback: {obs.metadata['feedback']}")

    print("\n[Negative Test 3]: Complete AI Hallucination (Totally Wrong)")
    obs = env.reset()
    bad_action_3 = LegalAction(
        simplified_text="The sky is blue today.",
        risk="SAFE",
        key_points=["apples", "oranges"]
    )
    obs = env.step(bad_action_3)
    print(f"Assigned Score: {obs.reward:.2f} / 1.00")
    print(f"Grader Feedback: {obs.metadata['feedback']}")
    
    env.close()

if __name__ == "__main__":
    asyncio.run(main())
