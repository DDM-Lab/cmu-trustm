# CMU TRUST’M

This is a simple server providing a JSON API, using FastAPI, to an IBL model for the TRUST’M project.

Note that as of 15 February 2023 this is just a crude, initial pass at such a thing. It’s goal
is not be anything even approximating the real thing, just a proof of concept that we can
successfully talk to one another

- The commands provide by this API just reflect the sort of offline models we’ve created to day
  and are surely not what we want for a real integration with Alfred the Butler. We will need to
  negotiate a better API for our real needs, which will probably involve a different structure
  to the interaction between Alfred the Butler and the model.

- There is essentially no error detection or handling. If calls are made passing data not
  formatted as expected, or in unexpected orders, there will be tears.

- The PyIBL model is just a stripped down, bare bones version of the one we’ve been using
  for the offline experiments, and is highly unlikely to do anything useful.

The goal here is like a dancing bear: the wonder isn’t how well it dances, it’s just that it dances at all.
Further iterations will be required to bring real joy to our hearts, but first steps first.

There are four calls to be made to this server: `start`, `query`, `mark` and `finish`. Each should be called
using the POST HTTP method, passing arguments as a JSON object.

All the JSON messages passed to these commands contains a field `user` which should be a non-empty string,
and describes the particular session currently at work.

### The `start` command

The `start` command (`http://localhost:8000/start`) supplies the PIR to be used, and resets the IBL model.
Its argument is of the form

    {"user": "<the user id goes here>",
     "name": "<the pir text goes here>"}

It returns nothing.

### The `query` command

The `query` command (`http://localhost:8000/query`) sends a description of a card, requesting the model’s
opinion of thumbs up, down or ignore. Its argument is of the form

    {"user": "<the user id goes here>",
     "id": "<a unquie ID as a string",
     "name": "<the name of this card's document>",
     "content": "<the text of this card's document>",
     "confidence": <the existing confidence score as a non-negative float>}

It returns a JSON object of the form

    {"user": "<the user id this was called with goes here>",
     "id": "<the same ID as was provided to this call>",
     "action": <a string one of "up", "down" or "ignore">,
     "confidence": {"up": <a number between 0 and 1, inclusive>,
                    "down": <a number between 0 and 1, inclusive>,
                    "ignore": <a number between 0 and 1, inclusive>}}

The three confidence values should sum to 1, and reflect the *model*’s confidence in these outcomes.
Typically the highest such value will correspond to the model’s prediction, but if there are ties
for the highest, a random choice is made; this typically occurs in the first few rounds before
the model has received much feedback.

### The `mark` command

The `mark` command (`http://localhost:8000/mark`) sends a user’s real thumbs up, down or ignore to the model.
Its argument is of the form

    {"user": "<the user id goes here>",
     "id": "<a card id>",
     "action": <a string one of "up", "down" or "ignore">}

To be useful the ID *must* be one that has been previously queried; if not, this is essentially a no-op.
It is possible to subsequently call `mark` again to change the mark on a card, if desired.
Note that the `start` command completely resets the model, forgetting all cards that may have been
previously seen.

It returns nothing.

Note that when the model starts, it is essentially guessing randomly. Until it has received feedback
of several of the user’s real choices it has no way of making informed decisions. Presumably one of
the ways we will attempt to improve this is with some sort of training scheme, but for now, this is
the way it is.

One can imagine that one way to hook this into Alfred the Butler is to start the model when a
user begins to interact with it, to query each card on a screenful when the screen is first shown,
to mark each card as the user marks them, and, when leaving a screen, to mark all the unmarked cards
as `"ignore"`. Note, however, that for such a process the IBL model will have nothing useful to say
for any cards on the first screen. Though the model is so wimpy, anyway, that.... Lot’s of room
for negotiation and improvement on all this.

### The `finish` command

The `finish` command (`http://localhost:8000/finish`) denotes the end of a session operating on
behalf of this user, and allows the space holding the user’s data to be reclaimed from memory.
Its argument is of the form

    {"user": "<the user id goes here>"}


## Running the model

Running `make build` builds a Docker container for running the model server.

Running `make run` runs this container, listening on port 8000.

For a trivial example, see `exercise_server.py`, which contains examples of each command.
Once the container is up and running you can confirm that it’s doing something by running
`python exercise_server.py`. This should print something like

    {'user': 'Elinor Dashwood',
     'id': 'card-0',
     'action': 'ignore',
     'confidence': {'up': 0.3333333333333333,
                    'down': 0.3333333333333333,
                    'ignore': 0.3333333333333333}}
    {'user': 'Elinor Dashwood',
     'id': 'card-1',
     'action': 'down',
     'confidence': {'up': 0.4960843783840418,
                    'down': 0.4960843783840418,
                    'ignore': 0.007831243231916345}}
    {'user': 'Elinor Dashwood',
     'id': 'card-2',
     'action': 'up',
     'confidence': {'up': 0.4916600224784701,
                    'down': 0.4916600224784701,
                    'ignore': 0.0166799550430598}}
    {'user': 'Elinor Dashwood',
     'id': 'card-3',
     'action': 'down',
     'confidence': {'up': 0.14161709283719434,
                    'down': 0.840225741341456,
                    'ignore': 0.018157165821349682}}


though each of the `action`s might be any of `"up"`, `"down"` or `"ignore"` instead, and the confidence
values will typically be different
