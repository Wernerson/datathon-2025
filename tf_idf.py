import os
import time
import errno

from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh.analysis import StemmingAnalyzer

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk

from ingestor import get_files

schema = Schema(
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

def ingest():
    nltk.download('stopwords')
    nltk.download('punkt')
    nltk.download('punkt_tab')

    make_sure_path_exists("./.whoosh")
    ix = create_in("./.whoosh", schema)
    writer = ix.writer()
    for filename, page_segments in get_files():
        print(f"Ingesting {filename} with {len(page_segments)} page segments...")
        for page in page_segments:
            content = page['text']
            url = page['url']
            writer.add_document(url=url, file=filename, content=content)
        print(f"Ingested {filename}.")
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
    print("Starting ingestion...")
    start = time.time()
    ingest()
    end = time.time()
    print(f"Ingestion complete! Took {end - start:.2f} seconds.")

if __name__ == "__main__":
        main()
