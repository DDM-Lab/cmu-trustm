# Copyright 2023 Carnegie Mellon University

import nltk

from fastapi import FastAPI
from nltk.corpus import stopwords
from nltk.tokenize import regexp_tokenize
from pydantic import BaseModel
from pyibl import Agent, bounded_linear_similarity

MISMATCH = 0.75
NOISE = 0.25
DECAY = 0.5

ACTIONS = ["up", "down", "ignore"]
MAX_CONFIDENCE = 30


nltk.download("stopwords")
stop_words = set(stopwords.words("english"))

def string_words(s):
    global stop_words
    return {w for w in regexp_tokenize(s.lower(), "[a-z0-9]{2,}")
            if w not in stop_words}

def word_count(target, probe):
    return len(target.intersection(probe)) / len(target)


class Pir(BaseModel):
    user: str
    name: str

class Card(BaseModel):
    user: str
    id: str | None = None
    name: str | None
    content: str | None = None
    confidence: float | None = None


class Response(BaseModel):
    user: str
    id: str
    action: str
    confidence: dict

class Feedback(BaseModel):
    user: str
    id: str
    action: str

class User(BaseModel):
    user: str


from pprint import pp

class State:

    def __init__(self, pir):
        self.pir = pir
        self.pir_words = string_words(pir.name or "")
        self.agent = Agent(["name_words",
                            "content_words",
                            "confidence",
                            "action"],
                           noise=NOISE,
                           decay=DECAY,
                           mismatch_penalty=MISMATCH)
        self.agent.similarity(["name_words"], bounded_linear_similarity(0, 1), 1)
        self.agent.similarity(["content_words"], bounded_linear_similarity(0, 1), 1)
        self.agent.similarity(["confidence"],
                              lambda x, y: 1 - (abs(max(min(x, MAX_CONFIDENCE), 0)
                                                    - max(min(y, MAX_CONFIDENCE), 0))
                                                / MAX_CONFIDENCE),
                              1)
        for action in ACTIONS:
            self.agent.populate([[1, 1, MAX_CONFIDENCE, action]], 1)
        self.card_map = {}

    def query(self, card):
        print("fuck?")
        pp(card)
        options = [[word_count(self.pir_words, string_words(card.name)),
                    word_count(self.pir_words, string_words(card.content)),
                    card.confidence,
                    action]
                   for action in ACTIONS]
        self.agent.details = True
        print("bugger?")
        choice = self.agent.choose(options)[-1]
        pp(self.agent.details)
        print("damn")
        det = self.agent.details[0]
        s = sum(d["blended"] for d in det)
        conf = {d["action"]: d["blended"] / s for d in det}
        pp(conf)
        self.card_map[card.id] = [choice, self.agent.respond()]
        print("here")
        return Response(user=self.pir.user, id=card.id, action=choice, confidence=conf)

    def mark(self, feedback):
        choice, df = self.card_map.get(feedback.id)
        if df is not None:
            df.update(int(feedback.action == choice))
        return None


states = {}

app = FastAPI()

@app.post("/start")
def start(pir: Pir):
    global states
    states[pir.user] = State(pir)

@app.post("/query")
def query(card: Card):
    global states
    try:
        return states[card.user].query(card)
    except Exception as e:
        # Long term we need to log stuff, including errors, and probably tell the caller
        # something has gone wrong, too.
        print("shit, piss and corruption")
        pp(e)
        pass

@app.post("/mark")
def mark(action: Feedback):
    global states
    try:
        return states[action.user].mark(action)
    except Exception:
        # Long term we need to log stuff, including errors, and probably tell the caller
        # something has gone wrong, too.
        pass

@app.post("/finish")
def finish(user: User):
    global states
    try:
        del states[user.user]
    except Exception:
        pass
