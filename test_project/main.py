from fastapi import FastAPI
from test_project.models import User, Post

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
