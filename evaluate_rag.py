# Query and Ground truth pairs including link
evaluation_dict = {
    "1": {
        "query": "What are the assisted living private rooms at covenantwood equipped with?",
        "link": "https://covenantwoods.com/health-services/assisted-living/",
        "answer": "Private bath with large walk-in shower (handicapped accessible), Large windows and plenty of natural light, Individually controlled lighting, heating, and air conditioning, Cable television and Wi-Fi service, Housekeeping and linen service, Emergency call system"
    },
    "2": {
        "query": "What therapy services do covenantwood offer?",
        "link": "https://covenantwoods.com/health-services/therapy-services/",
        "answer": "Specialized certifications and treatment, In-patient short-term rehabilitation to power your recovery, Convenient outpatient therapy services for Covenant Woods residents"
    },
    "3": {
        "query": "Who is part of the CovenantWood Management team?",
        "link": "https://covenantwoods.com/about-us/leadership/",
        "answer": "Thom Wright, President & CEO; Juanita Parks, CFO; etc."
    },
    "4": {
        "query": "What company provides assisted living near Richmond, Virginia?",
        "link": "---",
        "answer": "covenantwoods.com (and others possible)"
    },
    "5": {
        "query": "What companies uses packaging materials in Valencia, California?",
        "link": "---",
        "answer": "amsfulfillment.com (and others possible)"
    },
    "6": {
        "query": "Who uses Agile Methodologies to deal with Marketing in Fort Lauderdale, FL?",
        "link": "---",
        "answer": "starmark.com (and others possible)"
    },
    "7":{
        "query": "How many orders does amsfulfillment process per year?",
        "link": "https://www.amsfulfillment.com/",
        "answer": "8.36 million"
    },
    "8":{
        "query": "How can i contact American Cruise Lines?",
        "link": "https://www.americancruiselines.com/",
        "answer":"By phone 800-460-4518"
    },
    "9":{
        "query": "How can i contact American Cruise Lines?",
        "link": "https://www.americancruiselines.com/",
        "answer":"By phone 800-460-4518 or mail Inquiry@AmericanCruiseLines.com"
    },
    "10":{
        "query": "What classes of ships does American Cruise Lines have on offer?",
        "link": "https://www.americancruiselines.com/usa-riverboat-cruise-ships",
        "answer":" Patriot Class, Coastal Cats, Classic Paddlewheelers, Constellation Class Ships, Independence Class, and the only modern American Riverboats."
    },
    "11":{
        "query":"What is the bicoastal warehouse capacity of amsfulfillment?",
        "link": "https://www.amsfulfillment.com/",
        "answer":"over 1-million sqft of bi-coastal warehousing capacity (Delaware, Pennsylvania, California)"
    },
    "12":{
        "query":"What industries does amsfulfillment serve?",
        "link": "https://www.amsfulfillment.com/industries-served/",
        "answer":"Beauty products, Apparel, Fashion Accessories, Household goods, Supplement & Vitamins, Electronics, Books, Pet, and toys"
    },
    "13":{
        "query":"What fulfillment companies in the toy industry are located in Valencia California?",
        "link": "https://www.amsfulfillment.com/locations/",
        "answer":"amsfulfillment.com (and others possible)"
    }
}

import retrieve, agent

def evaluate():
    for key, value in evaluation_dict.items():
        query = value['query']
        link =value['link']
        answer = value['answer']

        db_responses = retrieve.query(query)
        # print(db_responses)

        response = agent.prompt_agent(query, strict_reg=False)

        print(f"User query: {query}")
        print(f"Retrieved Documents {[response[:75] for response in db_responses]}")
        print(f"Ground Truth example {answer}")
        print(f"Loose RAG answer {response}")


if __name__ == "__main__":
    evaluate()