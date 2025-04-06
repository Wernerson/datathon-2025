import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from agent import prompt_agent
app = FastAPI()


class Query(BaseModel):
    conversation: list[str] = [] # previous exchanges
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
    return prompt_agent(
        user_query=query.text,
        use_vector=query.vector,
        use_tfidf=query.inverted,
        use_ner=query.named,
        strict_reg=query.strict,
        conversation=query.conversation
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
