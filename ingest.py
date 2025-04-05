import torch

from vector_db import get_chromadb_collection

import os
import json

device = "cuda" if torch.cuda.is_available() else "cpu"

# Set OpenAI API Key
os.environ["OPENAI_API_KEY"] = "sk-svcacct-5yl4kJc9eQm7dpGPSEHhfqKBcMY7oGFs9XmqOVCldEAcn6RAuiMPYsnPJzT3IfZf_IM-RDJHB8T3BlbkFJkBYw7wr3U3cydg3k9fG43O5s4UYoRl_k2KPyOKP7se1TBsGPRzrriy6F"

def load_files(folder_path):
    files_in_folder = os.listdir(folder_path)
    len(files_in_folder)
    return files_in_folder


def load_documents(json_file):
    """Loads the JSON file."""
    with open(json_file, 'r', encoding="utf-8") as f:
      try:
          data = json.load(f)
          return data
      except json.JSONDecodeError:
          print(f"Error reading {json_file}, it may not be a valid JSON file.")
    return []


def segment_pages(docs):
    """You may prefer to load each page separately."""
    i = 0
    page_segment = []
    for s in list(docs['text_by_page_url'].values()):
      page_segment.append({"docID": docs['doc_id'], "pageID": 'page_' + str(i), "text": s})
      i += 1
    return page_segment


def store_chunks( files_in_folder, folder_path, chunk_size = 512):
    collection = get_chromadb_collection("my_collection")
    no_files = len(files_in_folder)
    for file_index, filename in enumerate(files_in_folder[:20]):
        if filename.endswith('.json'):

            document_segments = []
            ids = []
            file_path = os.path.join(folder_path, filename)
            doc = load_documents(file_path)
            page_segments = segment_pages(doc)
            for page in page_segments:
                content = page['text']
                doc_id = page['docID']
                page_id = page['pageID']

                for i in range(0, len(content), chunk_size):
                    segment = content[i: i + chunk_size]
                    document_segments.append(segment)
                    ids.append(f"{filename}/{doc_id}/{page_id}/chunk_{i}")
            print(f"Ingesting {filename} ({file_index + 1}/{no_files}) of length {len(document_segments)}...")
            for i in range(0, len(document_segments), 5461):
                collection.add(documents=document_segments[i: i + 5461], ids=ids[i: i + 5461])
            print(f"Ingested {filename} ({file_index+1}/{no_files})")


def main():
    print(f"Using device {device}...")
    folder_path = "./../data/hackathon_data"
    files_in_folder = load_files(folder_path)
    store_chunks(files_in_folder, folder_path, chunk_size = 4096)


if __name__ == "__main__":
        main()
