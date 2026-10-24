from fastapi import FastAPI, Depends, HTTPException, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import requests
import os

app = FastAPI()

# 1. Look for the Bearer token instead of X-API-Key
security = HTTPBearer()
EXPECTED_API_KEY = os.environ.get("LLM_API_KEY")

def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.credentials != EXPECTED_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return credentials.credentials

@app.get("/")
def read_root():
    return {"status": "online", "service": "llm-agent-server"}

# 2. Create the standard OpenAI endpoint Cline expects
@app.post("/v1/chat/completions", dependencies=[Depends(verify_api_key)])
async def openai_proxy(request: Request):
    body = await request.json()
    
    # 3. Forward the exact payload to Ollama's internal OpenAI engine
    try:
        response = requests.post("http://ollama:11434/v1/chat/completions", json=body)
        return JSONResponse(status_code=response.status_code, content=response.json())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))