def grade(action, ground_truth):
    score = 0.0

    decision = action.get("decision", "").lower()
    output = action.get("corrected_output", "").lower()

    gt_decision = ground_truth.get("decision", "").lower()

    # -----------------------------
    # 1. Decision correctness (0.5)
    # -----------------------------
    if decision == gt_decision:
        score += 0.5

    # ------------------------------------------
    # 2A. Exact output match (for structured tasks)
    # ------------------------------------------
    if "correct_output" in ground_truth:
        gt_output = ground_truth["correct_output"].lower()

        # Exact match → full score
        if gt_output == output:
            score += 0.5

        # Partial match → some score
        elif any(word in output for word in gt_output.split()):
            score += 0.25

    # ------------------------------------------
    # 2B. Keyword matching (for moderation task)
    # ------------------------------------------
    elif "keywords" in ground_truth:
        keywords = ground_truth["keywords"]

        matches = sum(1 for kw in keywords if kw in output)

        if matches > 0:
            score += 0.5 * (matches / len(keywords))

    # -----------------------------
    # Final clamp
    # -----------------------------
    return round(min(score, 1.0), 2)