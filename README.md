# datathon-2025

## Gieni by Bayes Brigade

> Checkout the live preview on [go.snb.li/datathon](go.snb.li/datathon)

## How to import data

- Vector DB
  - Make sure to `pip install torch tqdm chromadb` (or from requirements.txt)
  - Open `vector.py`
  - Modify the ranges you want to import on line 16 (not too many)
  - Run `vector.py`
  - This should create a `.chromadb` folder with the data
- Inverted Index
  - Make sure to `pip install whoosh nltk tqdm` (or from requirements.txt)
  - Open `tf_idf.py`
  - Modify the ranges you want to import on line 45 (by default the first 20)
  - Run `tf_idf.py`
  - This should create a `.whoosh` folder with the data
- Named Entity
  - Make sure to `pip install tqdm spacy sqlite3` (or from requirements.txt)
  - Run `python -m spacy download en_core_web_sm`
  - Open `named_entity_recognition.py`
  - Modify the range you want to import on line 41 (by default 20)
  - Run `named_entity_recognition.py`
  - This should create a `.sqlite.db` file with the data

## How to run simple queries

- Install all dependencies (from requirements.txt)
- Open `agent.py`
- Modify `user_query`
  - You can also pass several parameters to `prompt_agent`
  - `strict_reg=True`: if true, the agent only answers if it found relevant documents
  - `use_vector=True`: if true, uses vector db for retrieval (make sure to build/import before)
  - `use_tfidf=True`: if true, uses tf-idf inverted index for retrieval (make sure to build/import before)
  - `use_ner=False`: if true, uses NER for retrieval (make sure to build/import before)
- Run `agent.py`
- This will print a dict where `text` is the response and `sources` is the relevant correlating sources the answer is based on.

## How to run the UI

- Install dependencies (from requirements.txt)
- Open `api.py`
- Run `api.py`
- Goto `localhost:8000` and start prompting :)