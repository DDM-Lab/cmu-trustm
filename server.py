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
    name: str

class Card(BaseModel):
    id: str | None = None
    name: str | None
    content: str | None = None
    confidence: float | None = None


class Action(BaseModel):
    # used both for replies from the model and for supplying feedback to the model
    id: str
    action: str


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
        options = [[word_count(self.pir_words, string_words(card.name)),
                    word_count(self.pir_words, string_words(card.content)),
                    card.confidence,
                    action]
                   for action in ACTIONS]
        choice = self.agent.choose(options)[-1]
        self.card_map[card.id] = [choice, self.agent.respond()]
        return Action(id=card.id, action=choice)

    def mark(self, action):
        choice, df = self.card_map.get(action.id)
        if df is not None:
            df.update(int(action.action == choice))
        return None


state = None

app = FastAPI()

@app.post("/start")
def start(pir: Pir):
    global state
    state = State(pir)

@app.post("/query")
def query(card: Card):
    global state
    return state.query(card)

@app.post("/mark")
def mark(action: Action):
    global state
    state.mark(action)
