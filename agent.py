import retrieve

import openai
from openai import OpenAI

num_used_tokens = 0

def is_relevant_document(document, user_query, client):
    is_relevant_critic_prompt = document + "You are a critic that has to decide whether the document above is relevant for the following question, answer with exactly one word, (Accept) if the document above is relevant to answer the question, or (Reject), if the document is not useful to answer the question. Question: " + user_query + " Answer: ("
    response = client.responses.create(
        model="gpt-4o-mini",
        input = is_relevant_critic_prompt
    )

    global num_used_tokens
    num_used_tokens += response.usage.total_tokens

    #print(response)

    if(response.output_text.count("Accept") != 0):
        return True
    elif(response.output_text.count("Reject") != 0):
        return False
    else:
        #print("relevance critic provided invalid answer")
        return False



def is_valid_answer(answer, prompt, client):
    is_relevant_critic_prompt = prompt + "You are a critic that has to decide whether the following answer is a valid response to the question above, given the context provided. You specifically have to decide if the provided data allowed the agent to infer the given answer and if the answer provided accurately reflects the data, answer with exactly one word, (Accept) if and only if all the given information can be inferred from the data, or (Reject), if the answer is inaccurate or cannot be inferred from the data. Answer: " + answer + " Your Judgement: ("
    response = client.responses.create(
        model="gpt-4o-mini",
        input=is_relevant_critic_prompt
    )

    print(response)

    global num_used_tokens
    num_used_tokens += response.usage.total_tokens

    if (response.output_text.count("Accept") != 0):
        return True
    elif (response.output_text.count("Reject") != 0):
        return False
    else:
        #print("validity critic provided invalid answer")
        return False


def prompt_agent(user_query, strict_reg=True, use_vector: bool = True, use_tfidf: bool = True, use_ner: bool = False,
        strict: bool = False,
        conversation: list[str] = []):
    api_key = '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'

    client = OpenAI(api_key=api_key)

    conversation_history = "\n".join(conversation)

    #print("querying db")
    #TODO: rewrite querry dependent on the conversation history

    query_rewrite_prompt = "Conversation history: " + conversation_history + " Task: given the provided conversation history provided above, please rewrite the following user query in a way so that it is more likely to allow a Vectorized Database system to find the information the user wants to find. User query: " + user_query + " New Query: "

    query_rewrite_response = client.responses.create(
        model="gpt-4o-mini",
        input=query_rewrite_prompt
    )

    global num_used_tokens
    num_used_tokens += query_rewrite_response.usage.total_tokens

    print(query_rewrite_response.output)
    db_responses = retrieve.query(query_rewrite_response.output_text)

    filtered_db_responses = []
    for i in range(len(db_responses)):
        if len(db_responses[i]) > 10000:
            db_responses[i] = db_responses[i][:10000]





    # filter LLM
    context_documents = ""

    #print("filtering responses")
    for db_response in db_responses:
        if is_relevant_document(db_response, user_query, client):
            context_documents += db_response

    context_start = "This is the start of the context, $CONTEXT$: "

    context = context_start + context_documents

    if strict_reg:
        base_prompt = "You are a helpful AI Agent, only based on the context you were provided with, which is specified after $CONTEXT$, please answer the following question: "
    else:
        base_prompt = "You are a helpful AI Agent, please use the context above to help answer the following question: "

    prompt = context + base_prompt + user_query

    agent_responses = client.responses.create(
        model="gpt-4o-mini",
        input=prompt
    )

    num_used_tokens += agent_responses.usage.total_tokens

    # agent_responses = list()

    print(agent_responses)

    valid_responses = ""

    agent_responses = [agent_responses]

    for agent_response in agent_responses:
        agent_response_text = agent_response.output_text
        if is_valid_answer(agent_response_text, prompt, client):

            valid_responses += agent_response_text
            if not strict_reg:
                valid_responses += " the evaluator has specifically specified that this information is valid and is inferrable from the database"
        elif not strict_reg:
            valid_responses += agent_response_text + " the evaluator claims that this response may be inaccurate or at least cannot be inferred from the data"

    if len(valid_responses) == 0:
        valid_responses += "No valid answers! "

    # Reporter LLM
    if strict_reg:
        reporter_prompt = valid_responses + " Based on the potentially multiple valid answers above to the following question, if there were no valid answers, please respond with a message saying that you are sorry, but the question cannot be accurately answered with the information available, otherwise if there are multiple answers create a well formulated answer containing all the pieces of information provided in the valid answers above. Question: " + user_query + "Final Answer: "
    else:
        reporter_prompt = valid_responses + " Based on the potentially multiple answers above to the following question, create a well formulated answer containing all the pieces of information provided in the valid answers above. If the critic specified that the data may be inaccurate or not inferrable please specifically add the information that this specific part of the information is not exclusively based on database information, and spell out which parts of the information are subject to this warning. If the critic was fine with the data just answer the question. Please be brief and avoid redundant information. Question: " + user_query + "Final Answer: "


    reporter_response = client.responses.create(
        model="gpt-4o-mini",
        input=reporter_prompt
    )

    num_used_tokens += reporter_response.usage.total_tokens

    print(num_used_tokens)
    return reporter_response.output_text



def main():
    user_query = "What company provides assisted living near Richmond, Virginia?"
    agent_response = prompt_agent(user_query, False)

    print(agent_response)

if __name__ == "__main__":
    main()