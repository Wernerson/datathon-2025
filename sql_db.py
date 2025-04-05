
import sqlite3

DB_NAME = "./documents.db"

def insert_document_page(document_pages):
    """
    Document pages should be an array of tuples:
    (doc_id, page_id, raw_text)
    """
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.executemany("""
        INSERT INTO document_pages (doc_id, page_id, raw_text)
        VALUES (?, ?, ?)
    """, document_pages)
    con.commit()