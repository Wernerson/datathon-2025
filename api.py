import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from retrieve import query_with_sources

app = FastAPI()


class Query(BaseModel):
    text: str


@app.get("/")
def read_root():
    return FileResponse("index.html")


@app.post("/api/predict")
def predict(query: Query):
    return query_with_sources(query.text)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
