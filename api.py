import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from retrieve import query_with_sources

app = FastAPI()


class Query(BaseModel):
    text: str
    vector: bool = True
    inverted: bool = True
    named: bool = False
    strict: bool = False


@app.get("/")
def read_root():
    return FileResponse("index.html")


@app.post("/api/predict")
def predict(query: Query):
    return query_with_sources(
        query=query.text,
        use_vector=query.vector,
        use_tfidf=query.inverted,
        use_ner=query.named,
        strict=query.strict
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
