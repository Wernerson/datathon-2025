import retrieve

import openai
from openai import OpenAI


def is_relevant_document(document, user_query, client):

    is_relevant_critic_prompt = document + "You are a critic that has to decide whether the document above is relevant for the following question, answer with exactly one word, (Accept) if the document above is relevant to answer the question, or (Reject), if the document is not useful to answer the question. Question: " + user_query + " Answer: ("
    response = client.responses.create(
        model="gpt-4o-mini",
        input = is_relevant_critic_prompt
    )

    if(response.output_text.count("(Accept)" != 0)):
        return True
    elif(response.output_text.count("(Reject)" != 0)):
        return False
    else:
        print("relevance critic provided invalid answer")
        return False



def is_valid_answer(answer, prompt, client):
    is_relevant_critic_prompt = prompt + ("You are a critic that has to decide whether the following answer is a valid response to the question above, given the context provided. You specifically have to decide if the provided data is enough to give a valid answer and if the answer provided accurately reflects the data, answer with exactly one word, (Accept) if the following answer is Valid, or (Reject), if the answer is inaccurate or cannot be infered from the data. Answer: ") + answer + " Your Judgement: ("
    response = client.responses.create(
        model="gpt-4o-mini",
        input=is_relevant_critic_prompt
    )

    if (response.output_text.count("(Accept)" != 0)):
        return True
    elif (response.output_text.count("(Reject)" != 0)):
        return False
    else:
        print("relevance critic provided invalid answer")
        return False


def prompt_agent(user_query):

    db_responses = retrieve.query(user_query)

    api_key = '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'

    client = OpenAI(api_key=api_key)


    # filter LLM
    context_documents = ""

    for db_response in db_responses:
        if(is_relevant_document(db_response, user_query)):
            context_documents += db_response

    context_start = "This is the start of the context, $CONTEXT$: "

    context = context_start + context_documents

    base_prompt = "You are a helpful AI Agent, only only based on the context you were provided with which is specified after $CONTEXT$, please answer the following question: "

    prompt = context + base_prompt + user_query

    agent_responses = client.responses.create(
        model="gpt-4o-mini",
        input=prompt
    )

    # agent_responses = list()


    valid_responses = ""

    for agent_response in agent_responses:
        if is_valid_answer(agent_response, prompt):
            valid_responses += agent_response

    if len(valid_responses) == 0:
        valid_responses += "No valid answers! "

    # Reporter LLM
    reporter_prompt = valid_responses + "Based on the potentially multiple valid answers above to the following question, if there were no valid answers, please respond with a message saying that you are sorry, but the question cannot be accurately answered with the information available, otherwise if there are multiple answers create a well formulated answer containing all the pieces of information provided in the valid answers above. Question: " + user_query + "Final Answer: "

    reporter_response = client.responses.create(
        model="gpt-4o-mini",
        input=reporter_prompt
    )

    return reporter_response.output_text



def main():
    user_query = "What company provides sound Reinforcement Solutions near Cleveland?"
    agent_response = prompt_agent(user_query)

    print(agent_response)

if __name__ == "__main__":
    main()