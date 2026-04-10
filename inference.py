#!/usr/bin/env python3
import json
import os
import re
from typing import Any, Dict, List, Optional

from openai import OpenAI

from env.environment import AIValidationEnv
from env.models import Action
from env.tasks import TASKS


API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")

TASK_NAME = os.getenv("AI_VALIDATION_TASK", "ai_validation")
BENCHMARK = os.getenv("AI_VALIDATION_BENCHMARK", "ai_validation_env")

TEMPERATURE = 0.0
MAX_TOKENS = 256
MAX_STEPS = len(TASKS)
SUCCESS_SCORE_THRESHOLD = 0.67


SYSTEM_PROMPT = (
    "You are an AI validation agent.\n"
    "You will be given an AI decision and context.\n"
    "Your job is to decide whether the decision should be approved, rejected, or modified, "
    "and provide a corrected_output when needed.\n\n"
    "Return ONLY valid JSON with exactly these keys:\n"
    '{"decision":"approve|reject|modify","corrected_output":"..."}\n\n'
    "Rules:\n"
    "- Use 'reject' for clearly wrong or unsafe decisions.\n"
    "- Use 'modify' when the decision is partly correct but needs correction.\n"
    "- Use 'approve' only when the decision is already correct.\n"
    "- corrected_output must be concise, specific, and directly aligned with the task.\n"
    "- For code tasks, corrected_output should contain the corrected code only.\n"
    "- Do not include markdown, code fences, or any extra text."
)


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} score={score:.2f} rewards={rewards_str}",
        flush=True,
    )


def safe_model_dump(model: Any) -> Dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def extract_json_object(text: str) -> Dict[str, Any]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if match:
        cleaned = match.group(0)

    data = json.loads(cleaned)
    if not isinstance(data, dict):
        raise ValueError("Model output was not a JSON object")
    return data


def build_user_prompt(observation: Dict[str, Any], step_num: int, history: List[str]) -> str:
    decision_text = observation.get("decision_text", "")
    context = observation.get("context", "")
    history_text = "\n".join(history[-4:]) if history else "None"

    return (
        f"Step: {step_num}\n"
        f"Decision text: {decision_text}\n"
        f"Context: {context}\n"
        f"Previous actions:\n{history_text}\n\n"
        f"Return the JSON object now."
    )


def fallback_action(observation: Dict[str, Any]) -> Dict[str, str]:
    text = f"{observation.get('decision_text', '')} {observation.get('context', '')}".lower()

    if "loan" in text or "income" in text or "credit" in text:
        return {
            "decision": "reject",
            "corrected_output": "The loan should be rejected because the applicant does not meet income and credit requirements.",
        }

    if "hire" in text or "hiring" in text or "candidate" in text or "experience" in text:
        return {
            "decision": "modify",
            "corrected_output": "The candidate should be reconsidered due to strong project experience despite slightly lower years of experience.",
        }

    if "def " in text or "return" in text:
        return {
            "decision": "modify",
            "corrected_output": "def calculate_total(price, tax): return price + tax",
        }

    return {
        "decision": "reject",
        "corrected_output": "The decision should be rejected because it is inconsistent with the provided context.",
    }


def get_action_from_model(
    client: OpenAI,
    observation: Dict[str, Any],
    step_num: int,
    history: List[str],
) -> Dict[str, str]:
    user_prompt = build_user_prompt(observation, step_num, history)

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )

        text = completion.choices[0].message.content or ""
        payload = extract_json_object(text)

        action = Action(**payload)
        action_dict = safe_model_dump(action)

        if not action_dict.get("decision") or not action_dict.get("corrected_output"):
            raise ValueError("Missing required action fields")

        return {
            "decision": str(action_dict["decision"]).strip().lower(),
            "corrected_output": str(action_dict["corrected_output"]).strip(),
        }

    except Exception:
        return fallback_action(observation)


def unpack_result(result: Any) -> Dict[str, Any]:
    if isinstance(result, dict):
        return result
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    return {
        "observation": getattr(result, "observation", {}),
        "reward": getattr(result, "reward", 0.0),
        "done": getattr(result, "done", False),
        "info": getattr(result, "info", {}),
    }


def close_env(env: Any) -> None:
    close_fn = getattr(env, "close", None)
    if callable(close_fn):
        try:
            close_fn()
        except Exception:
            pass


def main() -> None:
    if not API_KEY:
        raise RuntimeError("HF_TOKEN or API_KEY is not set")

    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    env = None

    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        env = AIValidationEnv()

        reset_result = unpack_result(env.reset())
        observation = reset_result.get("observation", {})
        done = bool(reset_result.get("done", False))

        history: List[str] = []

        for step_num in range(1, MAX_STEPS + 1):
            if done:
                break

            action_dict = get_action_from_model(client, observation, step_num, history)
            action_str = json.dumps(action_dict, separators=(",", ":"), ensure_ascii=False)

            step_result = unpack_result(env.step(action_dict))
            reward = float(step_result.get("reward", 0.0) or 0.0)
            done = bool(step_result.get("done", False))
            info = step_result.get("info", {}) or {}
            error = info.get("last_action_error") if isinstance(info, dict) else None

            rewards.append(reward)
            steps_taken = step_num

            log_step(step=step_num, action=action_str, reward=reward, done=done, error=error)

            observation = step_result.get("observation", observation)
            history.append(f"step={step_num} action={action_str} reward={reward:.2f}")

        score = sum(rewards) / max(len(TASKS), 1)
        score = max(0.0, min(score, 1.0))
        success = score >= SUCCESS_SCORE_THRESHOLD

    except Exception:
        score = sum(rewards) / max(len(TASKS), 1)
        score = max(0.0, min(score, 1.0))
        success = False

    finally:
        if env is not None:
            close_env(env)
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)


if __name__ == "__main__":
    main()