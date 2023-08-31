# CMU TRUST’M

This is a simple server providing a JSON API, using FastAPI, to an IBL model for the TRUST’M project.

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
     "age": <the number of days since this content was published as a non-negative float>,
     "author": "<the author of this content>",
     "source": "<the source of this content>",
     "confidence": <the existing confidence score as a non-negative float>,
     “read": <a boolean, JSON true or false>}

The `read` member is optional, its absence is intended to be treated as the same as `false`;
it indicates whether or not the user has “opened” the card for further reading, though it provides
no information of how much the user may or may not have read of it.
.

#### Return value

The `query` command returns a JSON object of the form

    {"user": "<the user id this was called with goes here>",
     "id": "<the same ID as was provided to this call>",
     "action": <a string one of "up", "down" or "ignore">,
     "confidence": {"up": <a number between 0 and 1, inclusive>,
                    "down": <a number between 0 and 1, inclusive>,
                    "ignore": <a number between 0 and 1, inclusive>}}

The three confidence values sum to 1, and reflect the *model*’s confidence in these outcomes.
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

The `mark` command returns nothing.

Note that when the model starts, it is essentially guessing randomly. Until it has received feedback
of several of the user’s real choices it has no way of making informed decisions.

### The `advise` command

The `advise` command (`http://localhost:8000/advise`) sends an indication of attributes that
should figure more higly in the decision making for *this* user. Its argument is of the form

    {"user": "<the user id goes here>",
     "title_relevant": <a boolean, JSON true or false>,
     "content_relevant": <a boolean, JSON true or false>,
     "content_timely": <a boolean, JSON true or false>,
     "author_trustworthy": <a boolean, JSON true or false>,
     "source_trustworthy": <a boolean, JSON true or false>,
     "source_familiar": <a boolean, JSON true or false>}

All arguments other than `user` are optional. Those that are supplied and `true` have their
weights increased; Those that are `false` or absent do not.
The command can be called repeatedly, with the same or different values, to strengthen the
weight increase of the designated attributes.
Note that these weight increases are not shared between users.

#### Return value

The `advise` command returns a JSON object mapping attribute names to their weights, after any
adjustments made by the `advise` command, thus

    {'name': 2.5,
     'content': 1,
     'age': 1,
     'author': 1.5,
     'source': 1.5,
     'confidence': 2,
     'read': 2}

Note that the current weights can be queried by sending an `advise` with only the `id` argument.

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
