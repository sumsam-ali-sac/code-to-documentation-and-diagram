from fastapi import FastAPI
from autodoc.api.routes import router as api_router
import uvicorn
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="AutoDoc Service",
    description="Automatic documentation and diagram generation using LangGraph and Python Diagrams",
    version="0.1.0"
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to AutoDoc Service", "status": "running"}

if __name__ == "__main__":
    uvicorn.run("autodoc.main:app", host="0.0.0.0", port=8000, reload=True)
