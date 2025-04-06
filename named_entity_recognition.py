import time

import sqlite3
import spacy

from ingestor import get_file_pbar

# after pip install spacy, you also have to run this:
# python -m spacy download en_core_web_sm

RELEVANT_ENTITIES = {
    "PERSON": "person",  # People, including fictional.
    "NORP": "organisation",  # Nationalities or religious or political groups.
    "FAC": "location",  # Buildings, airports, highways, bridges, etc.
    "ORG": "organisation",  # Companies, agencies, institutions, etc.
    "GPE": "location",  # Countries, cities, states.
    "LOC": "location",  # Non-GPE locations, mountain ranges, bodies of water.
    "PRODUCT": "product",  # Objects, vehicles, foods, etc. (Not services.)
    "EVENT": "event",  # Named hurricanes, battles, wars, sports events, etc.
    "WORK_OF_ART": "product",  # Titles of books, songs, etc.
    "LAW": "product",  # Named documents made into laws.
    "LANGUAGE": "language",  # Any named language.
    # "DATE": "",  # Absolute or relative dates or periods.
    # "TIME": "",  # Times smaller than a day.
    # "PERCENT": "",  # Percentage, including ”%“.
    # "MONEY": "",  # Monetary values, including unit.
    # "QUANTITY",  # Measurements, as of weight or distance.
    # "ORDINAL": "",  # “first”, “second”, etc.
    # "CARDINAL": "",  # Numerals that do not fall under another type.
}


def ingest():
    nlp = spacy.load("en_core_web_sm")
    con = sqlite3.connect("./.sqlite.db")
    cur = con.cursor()

    cur.execute(f"CREATE TABLE IF NOT EXISTS entities (filename VARCHAR, url VARCHAR, type VARCHAR, name VARCHAR)")
    con.commit()

    pbar = get_file_pbar()
    for filename, page_segments in pbar:
        for page in page_segments:
            content = page['text']
            url = page['url']
            pbar.set_description(f"Ingesting {filename} - {url}")
            doc = nlp(content)
            for ent in doc.ents:
                if ent.label_ in RELEVANT_ENTITIES:
                    type = RELEVANT_ENTITIES[ent.label_]
                    cur.execute("INSERT INTO entities (filename, url, type, name) VALUES (?, ?, ?, ?)", (filename, url, type, ent.text))
    con.commit()


def get_relevant_docs_ner(query, n_results=5):
    con = sqlite3.connect("./.sqlite.db")
    cur = con.cursor()
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(query)
    clauses = []
    for ent in doc.ents:
        if ent.label_ in RELEVANT_ENTITIES:
            type = RELEVANT_ENTITIES[ent.label_]
            clauses.append((type, ent.text))
    clauses = " OR ".join([f"(type = '{type}' AND name = '{ent}')" for type, ent in clauses])
    sql_query = f"""
        SELECT filename, url FROM
        (SELECT filename, url, count(*) as count 
        FROM entities 
        WHERE {clauses}
        GROUP BY filename, url
        ORDER BY count DESC)
    """
    result = cur.execute(sql_query).fetchall()
    return result[:n_results]

def main():
    print("Starting ingestion...")
    start = time.time()
    ingest()
    end = time.time()
    print(f"Ingestion complete! Took {end - start:.2f} seconds.")

    print(get_relevant_docs_ner("What is in Pennsylvania?"))

if __name__ == "__main__":
    main()
