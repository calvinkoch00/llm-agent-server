from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import ollama
import os

app = FastAPI()

# Setup API Key security
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)
EXPECTED_API_KEY = os.environ.get("LLM_API_KEY")

class Prompt(BaseModel):
    text: str
    model: str = "llama3.2" 

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != EXPECTED_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

@app.get("/")
def read_root():
    return {"status": "online", "service": "llm-agent-server"}

# Inject the security dependency here
@app.post("/chat", dependencies=[Depends(verify_api_key)])
def chat_with_llm(prompt: Prompt):
    client = ollama.Client(host='http://ollama:11434')
    
    response = client.chat(model=prompt.model, messages=[
        {'role': 'user', 'content': prompt.text}
    ])
    
    return {
        "reply": response['message']['content'],
        "model_used": prompt.model
    }