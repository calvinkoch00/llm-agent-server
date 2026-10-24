from fastapi import FastAPI, Depends, HTTPException, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse, StreamingResponse
import requests
import os

app = FastAPI()

security = HTTPBearer()
EXPECTED_API_KEY = os.environ.get("LLM_API_KEY")

def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    if credentials.credentials != EXPECTED_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return credentials.credentials

@app.get("/")
def read_root():
    return {"status": "online", "service": "llm-agent-server"}

# 1. Added /v1/models endpoint for Cline
@app.get("/v1/models", dependencies=[Depends(verify_api_key)])
def get_models():
    try:
        response = requests.get("http://ollama:11434/v1/models")
        return JSONResponse(status_code=response.status_code, content=response.json())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2. Added live streaming support for code generation
@app.post("/v1/chat/completions", dependencies=[Depends(verify_api_key)])
async def openai_proxy(request: Request):
    body = await request.json()
    
    try:
        stream = body.get("stream", False)
        response = requests.post("http://ollama:11434/v1/chat/completions", json=body, stream=stream)
        
        # Catch Ollama errors (like "model still downloading") immediately
        if response.status_code != 200:
            return JSONResponse(status_code=response.status_code, content=response.json())

        # Stream the NDJSON chunks back to the IDE
        if stream:
            def generate():
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        yield chunk
            return StreamingResponse(generate(), media_type="text/event-stream")
        else:
            return JSONResponse(status_code=response.status_code, content=response.json())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))