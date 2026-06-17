import re


PATTERNS = {

    # =====================================================
    # PROMPT EXTRACTION
    # =====================================================

    "prompt_extraction": {

        "weight": 15,

        "patterns": [

            r"\breveal\b",
            r"\bshow\b",
            r"\bdisplay\b",
            r"\bprint\b",
            r"\bdump\b",
            r"\bexpose\b",
            r"\bleak\b",
            r"\boutput\b",

            r"tell me .* instructions",
            r"give me .* instructions",
            r"provide .* instructions",
        ]
    },

    # =====================================================
    # SENSITIVE TARGETS
    # =====================================================

    "sensitive_targets": {

        "weight": 25,

        "patterns": [

            r"system prompt",
            r"developer prompt",
            r"developer message",
            r"system message",

            r"hidden prompt",
            r"hidden instructions",

            r"internal instructions",
            r"internal prompt",

            r"guardrails",
            r"safety policy",
            r"safety rules",

            r"confidential instructions",
            r"secret instructions",

            r"initialization instructions",

            r"instructions that govern your behavior",

            r"rules that govern your behavior",

            r"behavior instructions",

            r"internal rules",

            r"model instructions",

            r"assistant instructions"
        ]
    },

    # =====================================================
    # OVERRIDE ATTEMPTS
    # =====================================================

    "override": {

        "weight": 20,

        "patterns": [

            r"ignore previous instructions",

            r"ignore all instructions",

            r"ignore system instructions",

            r"disregard previous instructions",

            r"forget previous instructions",

            r"override instructions",

            r"override system prompt",

            r"bypass restrictions",

            r"remove guardrails",

            r"disable safety"
        ]
    },

    # =====================================================
    # ROLEPLAY ATTACKS
    # =====================================================

    "roleplay": {

        "weight": 15,

        "patterns": [

            r"\bact as\b",

            r"\bpretend\b",

            r"\bsimulate\b",

            r"\broleplay\b",

            r"assume the role of",

            r"you are now",

            r"dan",

            r"developer mode",

            r"unrestricted ai",

            r"without limitations",

            r"without restrictions"
        ]
    },

    # =====================================================
    # PRETEXT ATTACKS
    # =====================================================

    "pretext": {

        "weight": 10,

        "patterns": [

            r"for compliance",

            r"for auditing",

            r"for audit purposes",

            r"for debugging",

            r"for testing",

            r"for evaluation",

            r"for verification",

            r"for research purposes",

            r"security assessment",

            r"red team exercise"
        ]
    },

    # =====================================================
    # ENCODING / OBFUSCATION
    # =====================================================

    "encoding": {

        "weight": 10,

        "patterns": [

            r"\bbase64\b",

            r"\bb64decode\b",

            r"\batob\(",

            r"\bfromcharcode\b",

            r"\bhex encoded\b",

            r"\bdecode this\b"
        ]
    },

    # =====================================================
    # TOOL ABUSE
    # =====================================================

    "tool_abuse": {

        "weight": 15,

        "patterns": [

            r"execute command",

            r"run shell",

            r"run bash",

            r"powershell",

            r"cmd\.exe",

            r"/bin/bash",

            r"api call",

            r"invoke tool",

            r"read file",

            r"open file"
        ]
    }
}


MAX_SCORE = 100


def regex_score(prompt):

    prompt = prompt.lower()

    total_score = 0

    matched_categories = []

    matched_patterns = []

    for category_name, category_data in PATTERNS.items():

        category_hit = False

        for pattern in category_data["patterns"]:

            if re.search(pattern, prompt):

                matched_patterns.append(pattern)

                category_hit = True

        if category_hit:

            total_score += category_data["weight"]

            matched_categories.append(
                category_name
            )

    total_score = min(
        total_score,
        MAX_SCORE
    )

    normalized_score = (
        total_score / 100.0
    )

    return {

        "score":
            normalized_score,

        "raw_score":
            total_score,

        "matched_categories":
            matched_categories,

        "matched_patterns":
            matched_patterns
    }


if __name__ == "__main__":

    while True:

        prompt = input("\nPrompt: ")

        result = regex_score(
            prompt
        )

        print("\nRegex Score:",
              result["raw_score"])

        print("\nCategories:")

        for category in result[
            "matched_categories"
        ]:
            print(
                "-",
                category
            )

        print("\nPatterns:")

        for pattern in result[
            "matched_patterns"
        ]:
            print(
                "-",
                pattern
            )