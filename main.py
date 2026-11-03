
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from gemini_service import generate_response
from guardrails import check_input

app = FastAPI(
    title="LLM Guardrails API",
    description="Gemini API with input guardrails",
    version="1.0.0"
)


class PromptRequest(BaseModel):
    prompt: str


@app.get("/")
def home():
    return {
        "message": "LLM Guardrails API is running!"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/generate")
def generate(request: PromptRequest):

    # Step 1: Check user input
    guardrail_result = check_input(request.prompt)

    # Step 2: Block unsafe prompts
    if not guardrail_result["allowed"]:
        return {
            "status": "blocked",
            "category": guardrail_result["category"],
            "message": guardrail_result["message"]
        }

    # Step 3: Send safe prompt to Gemini
    try:
        response = generate_response(request.prompt)

        return {
            "status": "success",
            "guardrail": guardrail_result,
            "response": response
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate response from Gemini."
        )
