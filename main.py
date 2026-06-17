import json
import os
from datetime import datetime, timezone

from fastapi import FastAPI
from pydantic import BaseModel

from detectors.decision import evaluate_prompt

app = FastAPI()

LOG_PATH = os.environ.get(
    "LOG_PATH",
    "./logs/events.json"
)

OLLAMA_URL = os.environ.get(
    "OLLAMA_URL",
    "http://localhost:11434/api/generate"
)

OLLAMA_MODEL = os.environ.get(
    "OLLAMA_MODEL",
    "qwen3:8b"
)

protection_enabled = True


class ChatRequest(BaseModel):
    prompt: str
    system_prompt: str = "You are a helpful assistant."


class ToggleRequest(BaseModel):
    enabled: bool


def write_log(entry: dict):

    os.makedirs(
        os.path.dirname(LOG_PATH),
        exist_ok=True
    )

    with open(LOG_PATH, "a") as f:
        f.write(
            json.dumps(entry) + "\n"
        )


@app.post("/toggle")
def toggle(data: ToggleRequest):

    global protection_enabled

    protection_enabled = data.enabled

    return {
        "protection_enabled": protection_enabled
    }


@app.get("/status")
def status():

    return {
        "protection_enabled": protection_enabled
    }


def call_ollama(prompt):
    pass


@app.post("/chat")
def chat(data: ChatRequest):

    global protection_enabled

    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    if not protection_enabled:

        llm_response = call_ollama(
            data.prompt
        )

        write_log({
            "timestamp": timestamp,
            "system_prompt": data.system_prompt,
            "user_input": data.prompt,
            "action_taken": "ALLOWED_UNGUARDED",
            "protection_enabled": False,
            "llm_response": llm_response
        })

        return {
            "status": "allowed",
            "response": llm_response
        }

    result = evaluate_prompt(
        data.prompt
    )

    log_entry = {
        "timestamp": timestamp,

        "system_prompt":
            data.system_prompt,

        "user_input":
            data.prompt,

        "action_taken":
            (
                "BLOCKED"
                if result["blocked"]
                else "ALLOWED"
            ),

        "protection_enabled":
            True,

        "risk_score":
            result["risk_score"],

        "avg_distance":
            result["avg_distance"],

        "min_distance":
            result["min_distance"],

        "regex_score":
            result["regex_score"],

        "regex_matches":
            result["regex_matches"],

        "nearest_attack":
            result["nearest_attack"],

        "top_distances":
            result["top_distances"]
    }

    if result["blocked"]:

        write_log(
            log_entry
        )

        return {
            "status": "blocked",
            "risk_score":
                result["risk_score"],

            "avg_distance":
                result["avg_distance"],

            "min_distance":
                result["min_distance"]
        }

    llm_response = call_ollama(
        data.prompt
    )

    log_entry[
        "llm_response"
    ] = llm_response

    write_log(
        log_entry
    )

    return {
        "status": "allowed",

        "risk_score":
            result["risk_score"],

        "avg_distance":
            result["avg_distance"],

        "min_distance":
            result["min_distance"],

        "response":
            llm_response
    }