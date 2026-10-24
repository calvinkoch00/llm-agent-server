from fastapi import FastAPI
from pydantic import BaseModel
import ollama

app = FastAPI()

class Prompt(BaseModel):
    text: str
    model: str = "llama3.2"  # Defaults to llama3.2 if not specified

@app.get("/")
def read_root():
    return {"status": "online", "service": "llm-agent-server"}

@app.post("/chat")
def chat_with_llm(prompt: Prompt):
    client = ollama.Client(host='http://ollama:11434')
    
    # Pass the dynamic model variable instead of hardcoding it
    response = client.chat(model=prompt.model, messages=[
        {'role': 'user', 'content': prompt.text}
    ])
    
    # Return the model name in the response so you know which one answered
    return {
        "reply": response['message']['content'],
        "model_used": prompt.model
    }