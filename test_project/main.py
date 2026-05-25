from fastapi import FastAPI

from test_project.models import Post, User

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}
