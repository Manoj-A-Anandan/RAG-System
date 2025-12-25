from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag import get_qa_chain
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Portfolio RAG Chatbot")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    message: str

@app.get("/")
def read_root():
    return {"status": "ok", "message": "RAG Chatbot Backend is running."}

@app.get("/diagnose")
def diagnose():
    try:
        if not os.path.exists("./data/portfolio_data.md"):
            return {"status": "error", "detail": "Portfolio data file not found."}
            
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            return {"status": "error", "detail": "GROQ_API_KEY not set."}
            
        # Try init
        from rag import get_qa_chain
        chain = get_qa_chain()
        if chain:
            return {"status": "ok", "detail": "RAG Chain (Groq + HF) initialized successfully."}
        else:
            return {"status": "error", "detail": "RAG Chain returned None."}
    except Exception as e:
        import traceback
        return {"status": "error", "detail": str(e), "traceback": traceback.format_exc()}

@app.post("/chat")
def chat_endpoint(query: Query):
    try:
        qa_chain = get_qa_chain()
        if not qa_chain:
             raise HTTPException(status_code=500, detail="RAG System not initialized (check data/keys).")
        
        # LCEL chain returns string directly
        print(f"Received query: {query.message}")
        result = qa_chain.invoke(query.message)
        print(f"Result: {result}")
        
        return {
            "answer": result,
            # "sources": [] # Sources not easily available in simple LCEL without extra steps
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {e}")
        # Build a safe error message
        if "GROQ_API_KEY" in str(e):
             raise HTTPException(status_code=500, detail="Configuration Error: GROQ Key missing.")
        if "429" in str(e):
             raise HTTPException(status_code=503, detail="Groq API Rate Limit. Please wait a minute.")
        raise HTTPException(status_code=500, detail=f"Internal Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
