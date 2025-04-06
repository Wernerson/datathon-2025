import time

import torch

from ingestor import get_file_pbar
from vector_db import get_chromadb_collection

HALF_CHUNK = 2048
MAX_BATCH_SIZE = 5461

device = "cuda" if torch.cuda.is_available() else "cpu"


def ingest():
    collection = get_chromadb_collection("my_collection")
    pbar = get_file_pbar(no_of_files=-1)
    for filename, page_segments in pbar:
        document_chunks = []
        ids = []
        metadata = []
        for page in page_segments:
            content = page['text']
            page_id = page['pageID']
            url = page['url']

            pbar.set_description(f"Counting chunks in {filename}/{page_id}")
            for i in range(0, len(content), HALF_CHUNK):
                chunk = content[i : i + 2*HALF_CHUNK]
                document_chunks.append(chunk)
                ids.append(f"{filename}/{page_id}/chunk_{i}")
                metadata.append({"url": url})

        pbar.set_description(f"Ingesting {filename} of length {len(document_chunks)}")
        for i in range(0, len(document_chunks), MAX_BATCH_SIZE):
            collection.add(
                documents=document_chunks[i: i + MAX_BATCH_SIZE],
                ids=ids[i: i + MAX_BATCH_SIZE],
                metadatas=metadata[i: i + MAX_BATCH_SIZE]
            )


def get_relevant_docs_vector(query, n_results=5):
    collection = get_chromadb_collection("my_collection")
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    for i in range(len(results["ids"][0])):
        id = results["ids"][0][i]
        metadata = results["metadatas"][0][i]
        file, page_id, chunk_id = id.split("/")
        url = metadata["url"]
        yield file, url


def main():
    print(f"Using device {device}.")
    print("Starting ingestion...")
    start = time.time()
    ingest()
    end = time.time()
    print(f"Ingestion complete! Took {end - start:.2f} seconds.")


if __name__ == "__main__":
    main()
