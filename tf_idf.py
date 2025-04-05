import os
import json
import time
import errno

from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh.analysis import StemmingAnalyzer

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk

schema = Schema(
    docId=ID(stored=True),
    url=ID(stored=True),
    file=ID(stored=True),
    content=TEXT(analyzer=StemmingAnalyzer())
)


def clean_query(query):
    stop_words = set(stopwords.words('english'))
    tokens = word_tokenize(query)
    filtered = [w for w in tokens if w.isalnum() and w.lower() not in stop_words]
    return " ".join(filtered)


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

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
    for url, text in docs['text_by_page_url'].items():
      page_segment.append({"docID": docs['doc_id'], "pageID": 'page_' + str(i), "url": url, "text": text})
      i += 1
    return page_segment


def ingest(files_in_folder, folder_path):
    nltk.download('stopwords')
    nltk.download('punkt')
    nltk.download('punkt_tab')

    make_sure_path_exists("./.whoosh")
    ix = create_in("./.whoosh", schema)
    writer = ix.writer()
    no_files = len(files_in_folder)
    for file_index, filename in enumerate(files_in_folder[:20]):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            doc = load_documents(file_path)
            page_segments = segment_pages(doc)
            print(f"Ingesting {filename} ({file_index + 1}/{no_files}) of length {len(page_segments)}...")
            for page in page_segments:
                content = page['text']
                doc_id = page['docID']
                url = page['url']
                writer.add_document(docId=doc_id, url=url, file=filename, content=content)
            print(f"Ingested {filename} ({file_index+1}/{no_files})")
    writer.commit()


def get_relevant_docs_tfidf(query, n_results=5):
    ix = open_dir("./.whoosh")
    with ix.searcher() as searcher:
        cleaned_query = clean_query(query)
        parsed_query = QueryParser("content", ix.schema).parse(cleaned_query)
        result = searcher.search(parsed_query, limit=n_results)
        for hit in result:
            yield hit["file"], hit["url"]


def main():
    folder_path = "./.data"
    files_in_folder = load_files(folder_path)

    print("Starting ingestion...")
    start = time.time()
    ingest(files_in_folder, folder_path)
    end = time.time()
    print(f"Ingestion complete! Took {end - start:.2f} seconds.")

    print(get_relevant_docs_tfidf("Name me companies in Pennsylvania that manufactures heat pipes."))

if __name__ == "__main__":
        main()
