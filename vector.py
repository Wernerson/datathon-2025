import torch
import time

from ingestor import get_files
from vector_db import get_chromadb_collection

CHUNK_SIZE = 4096

device = "cuda" if torch.cuda.is_available() else "cpu"


def ingest():
    collection = get_chromadb_collection("my_collection")
    for filename, page_segments in get_files():
        document_segments = []
        ids = []
        metadata = []
        for page in page_segments:
            content = page['text']
            page_id = page['pageID']
            url = page['url']

            for i in range(0, len(content), CHUNK_SIZE):
                segment = content[i: i + CHUNK_SIZE]
                document_segments.append(segment)
                ids.append(f"{filename}/{page_id}/chunk_{i}")
                metadata.append({"url": url})
        print(f"Ingesting {filename} of length {len(document_segments)}...")
        for i in range(0, len(document_segments), 5461):
            collection.add(documents=document_segments[i: i + 5461], ids=ids[i: i + 5461],
                           metadatas=metadata[i: i + 5461])
        print(f"Ingested {filename}")


def get_relevant_docs_vector(query, n_results=5):
    collection = get_chromadb_collection("my_collection")
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    for i in range(len(results["ids"][0])):
        id = results["ids"][0][i]
        metadata = results["metadatas"][0][i]
        file, doc_id, page_id, chunk_id = id.split("/")
        url = metadata["url"]
        yield file, url


def main():
    print(f"Using device {device}...")
    print("Starting ingestion...")
    start = time.time()
    ingest()
    end = time.time()
    print(f"Ingestion complete! Took {end - start:.2f} seconds.")


if __name__ == "__main__":
    main()
