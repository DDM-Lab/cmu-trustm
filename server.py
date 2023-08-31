# Copyright 2023 Carnegie Mellon University

import nltk

from fastapi import FastAPI
from nltk.corpus import stopwords
from nltk.tokenize import regexp_tokenize
from pprint import pp
from pydantic import BaseModel
from pyibl import Agent, bounded_linear_similarity, positive_linear_similarity

MISMATCH = 0.75
NOISE = 0.25
DECAY = 0.5

ACTIONS = ["up", "down", "ignore"]
MAX_CONFIDENCE = 30
WEIGHT_INCREMENT = 0.5

NO_MATCH = "455D3DEC8638C16A625A1E24BBA4EE4092BE9D3" # a string that should match no real author or source

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
    age: float | None = None
    author: str | None = None
    source: str | None = None
    confidence: float | None = None
    read: bool = False

class Response(BaseModel):
    user: str
    id: str
    action: str
    confidence: dict

class Feedback(BaseModel):
    user: str
    id: str
    action: str

class Weights(BaseModel):
    user: str
    title_relevant: bool = False
    content_relevant: bool = False
    content_timely: bool = False
    author_trustworthy: bool = False
    source_trustworthy: bool = False
    source_familiar: bool = False

class User(BaseModel):
    user: str


class State:

    def __init__(self, pir):
        self.pir = pir
        self.pir_words = string_words(pir.name or "")
        self.agent = Agent(["name",
                            "content",
                            "age",
                            "author",
                            "source",
                            "confidence",
                            "read",
                            "action"],
                           noise=NOISE,
                           decay=DECAY,
                           mismatch_penalty=MISMATCH)
        for action in ACTIONS:
            self.agent.populate([[1, 1, 1, NO_MATCH, NO_MATCH, MAX_CONFIDENCE, True, action]], 1)
        self.weights = {"name": 2,
                        "content": 1,
                        "age": 1,
                        "author": 1,
                        "source": 1,
                        "confidence": 2,
                        "read": 2}
        self.set_similarity()
        self.card_map = {}

    def set_similarity(self):
        wsum = sum(self.weights.values())
        def setsim(k, f):
            self.agent.similarity([k], f, self.weights[k] / wsum)
        setsim("name", bounded_linear_similarity(0, 1))
        setsim("content", bounded_linear_similarity(0, 1))
        setsim("age", lambda x, y: 0 if x is None or y is None else positive_linear_similarity(x, y))
        setsim("author", True)
        setsim("source", True)
        setsim("confidence", lambda x, y: 1 - (abs(max(min(x, MAX_CONFIDENCE), 0)
                                                   - max(min(y, MAX_CONFIDENCE), 0))
                                               / MAX_CONFIDENCE))
        setsim("read", True)

    def query(self, card):
        options = [[word_count(self.pir_words, string_words(card.name)),
                    word_count(self.pir_words, string_words(card.content)),
                    card.age,
                    card.author,
                    card.source,
                    card.confidence,
                    card.read,
                    action]
                   for action in ACTIONS]
        self.agent.details = True
        choice = self.agent.choose(options)[-1]
        det = self.agent.details[0]
        s = sum(d["blended"] for d in det)
        conf = {d["action"]: d["blended"] / s for d in det}
        self.card_map[card.id] = [choice, self.agent.respond()]
        return Response(user=self.pir.user, id=card.id, action=choice, confidence=conf)

    def mark(self, feedback):
        choice, df = self.card_map.get(feedback.id)
        if df is not None:
            df.update(int(feedback.action == choice))
        return None

    def advise(self, weights):
        if weights.title_relevant:
            self.weights["name"] += WEIGHT_INCREMENT
        if weights.content_relevant:
            self.weights["content"] += WEIGHT_INCREMENT
        if weights.content_timely:
            self.weights["age"] += WEIGHT_INCREMENT
        if weights.author_trustworthy:
            self.weights["author"] += WEIGHT_INCREMENT
        if weights.source_trustworthy or weights.source_familiar:
            self.weights["source"] += WEIGHT_INCREMENT
        self.set_similarity()
        return self.weights


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
        print("Exception detected in query")
        pp(e)

@app.post("/mark")
def mark(action: Feedback):
    global states
    try:
        return states[action.user].mark(action)
    except Exception:
        print("Exception detected in mark")
        pp(e)

@app.post("/advise")
def advise(attributes: Weights):
    global states
    try:
        return states[attributes.user].advise(attributes)
    except Exception:
        print("Exception detected in advise")
        pp(e)

@app.post("/finish")
def finish(user: User):
    global states
    try:
        del states[user.user]
    except Exception:
        print("Exception detected in finish")
        pp(e)
