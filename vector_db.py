import chromadb
import torch

from chromadb.utils import embedding_functions

SENTENCE_TRANSFORMER_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHROMA_PATH = "./.chroma"
device = "cuda" if torch.cuda.is_available() else "cpu"


def get_chromadb_collection(name: str):
    embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=SENTENCE_TRANSFORMER_EMBEDDING_MODEL,
        device=device,
        normalize_embeddings=True
    )
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(name, embedding_function=embedding_func)
