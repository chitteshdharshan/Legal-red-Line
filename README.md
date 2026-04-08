---
title: Legal Red Line
emoji: ⚖️
colorFrom: red
colorTo: gray
sdk: docker
pinned: false
---

# Legal Red Line: OpenEnv RL Challenge

An OpenEnv environment simulating a real-world task for AI Legal Assistants.

## ⚖️ Environment Description
The **Legal Red Line** environment challenges an agent to act as a legal reviewer. Given a complex legal clause, the agent must:
1. **Simplify**: Translate legalese into plain English without losing meaning.
2. **Risk Detection**: Classify the clause as `SAFE` (standard/low risk) or `NOT SAFE` (contains obligations, penalties, or unusual risk).
3. **Key Point Extraction**: Identify the core obligations or conditions.

### Motivation
Legal review is a high-value, real-world task that requires nuanced understanding and precise formatting. This environment benchmarks an agent's ability to handle domain-specific language and follow strict output constraints.

## 🛠 Space Definitions

### Observation Space
- `clause`: The raw legal text.
- `history`: Feedback from previous attempts in the episode.
- `task_name`: Identifier for the current task.

### Action Space
The agent must provide a JSON object:
- `simplified_text` (string): Plain English version.
- `risk` (string): `SAFE` or `NOT SAFE`.
- `key_points` (list of strings): Bulleted obligations.

### Reward Function
The reward (0.0 - 1.0) is calculated based on:
- **Format Validity (10%)**: Successful Pydantic parsing.
- **Risk Classification (30%)**: Matching the ground truth label.
- **Key Points Coverage (30%)**: Presence of mandatory semantic keywords in the extracted points.
- **Simplification Accuracy (30%)**: Overlap with essential simplified concepts.

## 📋 Tasks

| Task Name | Difficulty | Description |
|-----------|------------|-------------|
| `late_payment_penalty` | Easy | Single obligation regarding 5% late fees. |
| `termination_notice` | Medium | Notice periods and "without cause" termination fees. |
| `indemnification_complexity` | Hard | Complex third-party claims and "gross negligence" carve-outs. |

## 🚀 Setup and Usage

### Local Development
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run baseline inference:
   ```bash
   export HF_TOKEN="your-api-key"
   python inference.py
   ```

### Docker
```bash
docker build -t legal-red-line .
docker run -p 7860:7860 legal-red-line
```

## 📊 Baseline Scores (GPT-4o)
- **Late Payment**: 1.00
- **Termination**: 0.90
- **Indemnification**: 0.85
- **Average**: 0.91

---
Tag: `openenv`
