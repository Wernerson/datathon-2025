from vector_db import get_chromadb_collection

def query_db(query, n_results = 5):
    collection = get_chromadb_collection("my_collection")
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    print(results)


def main():
    query_db(query = "I'm looking for a ")

if __name__ == "__main__":
    main()