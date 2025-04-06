import os
import json
from tqdm import tqdm

DATA_PATH = "./../data/hackathon_data_reduced"


def load_files(folder_path):
    files_in_folder = os.listdir(folder_path)
    len(files_in_folder)
    return files_in_folder


def load_document(json_file):
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
    for url, text in docs['text_by_page_url'].items():
      page_segment.append({"pageID": 'page_' + str(i), "url": url, "text": text})
      i += 1
    return page_segment


def file_generator(files):
    for file_index, filename in enumerate(files):
        if filename.endswith('.json'):
            file_path = os.path.join(DATA_PATH, filename)
            doc = load_document(file_path)
            page_segments = segment_pages(doc)
            yield filename, page_segments

def get_file_pbar(start_files = 0,end_files = 20):
    files_in_folder = load_files(DATA_PATH)
    files = files_in_folder[start_files:end_files]
    return tqdm(file_generator(files), total=len(files))