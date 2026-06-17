from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import json
from detectors.decision import evaluate_prompt


class PromptInjectionMiddleware(BaseHTTPMiddleware):
    """Middleware to detect and block prompt injection attacks."""
    
    async def dispatch(self, request: Request, call_next):
        if request.method == "POST" and request.url.path == "/chat":
            try:
                body = await request.body()
                data = json.loads(body)
                prompt = data.get("prompt", "")
                
                if prompt:
                    result = evaluate_prompt(prompt)
                    
                    if result["blocked"]:
                        return JSONResponse(
                            status_code=403,
                            content={
                                "error": "Prompt injection detected",
                                "decision": "BLOCKED",
                                "risk_score": result["risk_score"],
                                "regex_matches": result["regex_matches"],
                            }
                        )
                    
                    request.state.prompt_evaluation = result
            except:
                pass
        
        response = await call_next(request)
        return response
