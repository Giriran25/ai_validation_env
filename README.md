---

title: AI Validation Environment
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
app_file: main.py
pinned: false

---

# 🧠 AI Decision Validation & Correction Environment

## 🚀 Overview

This project is an OpenEnv-based environment that simulates real-world scenarios where AI systems make decisions, and an agent must validate and correct them.

It enables:

* Evaluation of AI-generated decisions
* Detection of incorrect or unsafe outputs
* Correction suggestions
* Reward-based scoring (0.0–1.0)

---

## 🌍 Real-World Problems Covered

* 🏦 Loan approval validation
* 💼 Hiring decision correction
* 💻 Code logic correction
* 🛡️ Content moderation

---

## 🧩 Tasks

| Task               | Description                      | Difficulty |
| ------------------ | -------------------------------- | ---------- |
| Loan Validation    | Detect incorrect loan approvals  | Easy       |
| Hiring Decision    | Evaluate biased hiring decisions | Medium     |
| Code Correction    | Fix incorrect code logic         | Hard       |
| Content Moderation | Detect harmful content           | Medium     |

---

## ⚙️ Environment Design

### 📥 Observation Space

```json
{
  "decision_text": "string",
  "context": "string"
}
```

---

### 📤 Action Space

```json
{
  "decision": "approve | reject | modify",
  "corrected_output": "string"
}
```

---

## 🎯 Reward Function

* +0.5 → Correct decision
* +0.5 → Correct or partially correct output
* Supports partial matching
* Final reward range: **0.0 – 1.0**

---

## ▶️ Running Locally

### 1. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

---

### 2. Install dependencies

```bash
pip install fastapi uvicorn pydantic openai openenv-core
```

---

### 3. Run API

```bash
uvicorn main:app --reload
```

Open:

```
http://127.0.0.1:8000/docs
```

---

### 4. Run inference

```bash
python inference.py
```

---

## 🐳 Docker Usage

### Build

```bash
docker build -t ai-validation-env .
```

---

### Run

```bash
docker run -p 7860:7860 ai-validation-env
```

---

## 🔐 Environment Variables

Set these before running:

```bash
HF_TOKEN=your_token_here
API_BASE_URL=https://router.huggingface.co/v1
MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
```

---

## 📊 Baseline Output

Example:

```
[START]
[STEP] step=1 ...
[STEP] step=2 ...
[STEP] step=3 ...
[STEP] step=4 ...
[END] score=0.8
```

---

## ✅ OpenEnv Compliance

* ✔ step(), reset(), state() implemented
* ✔ 4 tasks with graders
* ✔ Deterministic scoring
* ✔ Multi-mode deployment ready
* ✔ openenv validate passed

---

## 🏆 Impact

This system enables:

* 🤖 AI validating AI decisions
* ⚡ Reduced human intervention
* 🔒 Safer automated systems
* 📈 Scalable evaluation pipelines

---

## 👨‍💻 Author

Ranjith Kumar G
Yashwanth K
Shravan singh
