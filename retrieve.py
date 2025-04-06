import json
from openai import OpenAI

from vector import get_relevant_docs_vector
from tf_idf import get_relevant_docs_tfidf
from named_entity_recognition import get_relevant_docs_ner


INSTRUCTIONS = """
    You are an AI assistant to a Supply Chain Director.
    Your task is to answer their question with the information provided above as accurately and precisely as possible.
    Only use the context provided to you to answer the questions.
    If the context does not provide the required information, respond with the fact that you are unable to answer the question with the provided context.
"""


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

    relevant_docs = set()
    for doc in get_relevant_docs_vector(query, n_results=5):
        relevant_docs.add(doc)

    for doc in get_relevant_docs_tfidf(query, n_results=5):
        relevant_docs.add(doc)

    for doc in get_relevant_docs_ner(query, n_results=5):
        relevant_docs.add(doc)

    context = []
    for file, url in relevant_docs:
        document = get_document(file)
        text = document["text_by_page_url"][url]
        context.append(f"Excerpt from {url}:\n{text}")

    return context

    # print(len(context))
    # response = client.responses.create(
    #     model="gpt-4o-mini",
    #     instructions="\n".join(context) + "\n" + INSTRUCTIONS,
    #     input=query,
    # )
    # return response.output_text


def query_with_sources(
        query: str,
        use_vector: bool = True, use_tfidf: bool = True, use_ner: bool = False,
        strict: bool = False,
        conversation: list[str] = []
):
    client = OpenAI(
        api_key="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",
    )

    relevant_docs = set()
    if use_vector:
        for doc in get_relevant_docs_vector(query, n_results=1):
            relevant_docs.add(doc)

    if use_tfidf:
        for doc in get_relevant_docs_tfidf(query, n_results=1):
            relevant_docs.add(doc)

    if use_ner:
        for doc in get_relevant_docs_ner(query, n_results=1):
            relevant_docs.add(doc)

    # context = []
    # for file, url in relevant_docs:
    #     document = get_document(file)
    #     text = document["text_by_page_url"][url]
    #     context.append(f"Excerpt from {url}:\n{text}")

    # response = client.responses.create(
    #     model="gpt-4o-mini",
    #     instructions="\n".join(context) + "\n" + INSTRUCTIONS,
    #     input=query,
    # )
    # return response.output_text
    print(conversation)
    response_text = "This is a response text..."
    return {
        "text": response_text,
        "sources": [url for _, url in relevant_docs]
    }


def main():
    print(query("What company provides sound Reinforcement Solutions near Cleveland?"))
    print(query("What company creates heat pumps in Pennsylvania?"))
    print(query("Are there aluminum auto manufacturers in southern Italy?"))


if __name__ == "__main__":
    main()
