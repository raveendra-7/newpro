from detectors.decision import evaluate_prompt

print("PromptGuard Calibration Tester")

while True:

    prompt = input("\nPrompt: ")

    if prompt.lower() in [
        "exit",
        "quit"
    ]:
        break

    result = evaluate_prompt(
        prompt
    )

    print("\n")

    print(
        "Decision:",
        result["decision"]
    )

    print(
        "Risk Score:",
        result["risk_score"]
    )

    print(
        "\nClosest Attack:"
    )

    print(
        result["nearest_attack"]
    )

    print(
        "\n" + "=" * 60
    )
