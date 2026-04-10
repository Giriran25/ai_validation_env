TASKS = [
    {
        "id": "easy",
        "decision_text": "AI loan approval system approved a loan for a user with no income and no prior credit history.",
        "context": "Bank policy requires stable income and a minimum credit score of 650 for loan approval.",
        "ground_truth": {
            "decision": "reject",
            "correct_output": "The loan should be rejected because the applicant does not meet income and credit requirements."
        }
    },
    {
        "id": "medium",
        "decision_text": "AI hiring system rejected a candidate with 2 years of experience for a role requiring 3 years, ignoring their strong project portfolio.",
        "context": "Company policy allows flexibility in experience if candidates demonstrate strong practical skills.",
        "ground_truth": {
            "decision": "modify",
            "correct_output": "The candidate should be reconsidered due to strong project experience despite slightly lower years of experience."
        }
    },
    {
        "id": "hard",
        "decision_text": "def calculate_total(price, tax): return price - tax",
        "context": "The function should correctly calculate the total price including tax.",
        "ground_truth": {
            "decision": "modify",
            "correct_output": "def calculate_total(price, tax): return price + tax"
        }
    },
    {
    "id": "content_moderation",
    "difficulty": "medium",
    "decision_text": "AI allowed a post containing hate speech targeting a specific community.",
    "context": "Platform policy strictly prohibits hate speech and harmful content.",
    "ground_truth": {
        "decision": "reject",
        "keywords": ["hate", "policy", "violation", "harmful"]
    }
}
]