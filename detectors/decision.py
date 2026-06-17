from detectors.regex_detector import regex_score
from detectors.semantics import semantic_search


REGEX_WEIGHT = 0.3  
SEMANTIC_WEIGHT = 0.7

BLOCK_THRESHOLD = 50


def evaluate_prompt(prompt):

    regex_result = regex_score(
        prompt
    )

    semantic_result = semantic_search(
        prompt,
        top_k=10
    )

    regex_value = (
        regex_result["score"]
        * 100
    )

    semantic_value = (
        semantic_result["semantic_score"]
    )

    risk_score = (

        regex_value
        * REGEX_WEIGHT

        +

        semantic_value
        * SEMANTIC_WEIGHT
    )

    risk_score = round(
        risk_score,
        2
    )

    blocked = (
        risk_score >=
        BLOCK_THRESHOLD
    )

    return {

        "blocked":
            blocked,

        "decision":
            "BLOCK"
            if blocked
            else
            "ALLOW",

        "risk_score":
            risk_score,

        "nearest_attack":
            semantic_result[
                "nearest_attack"
            ]
    }