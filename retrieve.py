import json
from openai import OpenAI

from vector_db import get_chromadb_collection

INSTRUCTIONS = """
    You are an AI assistant to a Supply Chain Director.
    Your task is to answer their question with the information provided above as accurately and precisely as possible.
    Only use the context provided to you to answer the questions.
    If the context does not provide the required information, respond with the fact that you are unable to answer the question with the provided context.
"""


def get_relevant_docs(query, n_results=5):
    collection = get_chromadb_collection("my_collection")
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    return results


def get_document(file_name):
    json_file = f"./../data/hackathon_data_reduced/{file_name}"
    with open(json_file, 'r', encoding="utf-8") as f:
        try:
            data = json.load(f)
            return data
        except json.JSONDecodeError:
            print(f"Error reading {json_file}, it may not be a valid JSON file.")
    return None


def query(query):
    client = OpenAI(
        api_key="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",
    )

    context = []
    relevant_docs = get_relevant_docs(query, n_results=5)
    for i in range(len(relevant_docs["ids"][0])):
        id = relevant_docs["ids"][0][i]
        metadata = relevant_docs["metadatas"][0][i]
        file, page_id, chunk_id = id.split("/")
        print(file)
        document = get_document(file)
        text = document["text_by_page_url"][metadata["url"]]
        context.append(f"Excerpt from {metadata["url"]}:\n{text}")

    # response = client.responses.create(
    #     model="gpt-4o-mini",
    #     instructions="\n".join(context) + "\n" + INSTRUCTIONS,
    #     input=query,
    # )
    #
    # print(response.output_text)


def main():
    query("What company provides sound Reinforcement Solutions near Cleveland?")


if __name__ == "__main__":
    main()
