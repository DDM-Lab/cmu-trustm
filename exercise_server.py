from itertools import count
from pprint import pp
import requests

def send_receive(msg, **data):
    return requests.post(f"http://localhost:8000/{msg}",
                         json=({"user": "Elinor Dashwood"} | data)).json()

send_receive("start", user="Elinor Dashwood", name="How to mumble a fuchsia stacked snorkel")

for i, (name, content, confidence, read, ground_truth) in zip(count(), [
        ["Fuchsia Snorkels Stack Brilliantly",
         "Lorem ipsum dolor sit amet, consectetur fuchsia adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim snorkel veniam, quis stack nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non snorkel proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
         137.036,
         True,
         "up"],
        ["Flippers Aligned Badly in Purple Water",
         "Integer maximus consequat hendrerit. In hac habitasse platea dictumst. Nullam ultricies, purus et auctor iaculis, nunc ipsum aliquam nisl, vitae molestie lectus massa sit amet turpis. Pellentesque at euismod nisl. Proin magna nibh, auctor vel dolor at, cursus convallis odio. Proin ullamcorper purus ornare, elementum velit eu, viverra ante. Maecenas quis justo sem. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Cras condimentum mauris et metus accumsan, vel elementum enim gravida.",
         1.61803,
         False,
         "down"],
        ["Frothy Fuschia Feigns Fright",
         "Nullam non sodales ante, ac fringilla odio. Aenean eget elit tortor. Duis eros quam, dignissim non magna vel, suscipit auctor lorem. Mauris faucibus, est ut interdum ultrices, urna tortor fringilla enim, ut rhoncus justo tellus placerat nulla. In et metus venenatis, commodo sapien vitae, pharetra ipsum. Integer eu lorem vitae risus varius lacinia sed consequat leo. Nullam vel feugiat erat.",
         2.71828,
         False,
         "ignore"],
        ["Stack Stacks of Stacked Stack Stacks",
         "Vivamus rutrum magna eget neque gravida dictum. Sed mauris metus, cursus at lorem sed, faucibus rhoncus erat. Ut venenatis consequat blandit. Aliquam fermentum mattis tristique. Nunc tincidunt ipsum vitae dui sagittis lobortis. Aliquam turpis nisl, pellentesque nec facilisis quis, mattis et tortor. Proin ultricies erat at turpis dignissim sodales. Nunc sit amet mollis augue, quis fringilla tellus. Nunc hendrerit nisl mauris. Aenean lacinia porttitor ligula. Maecenas libero ligula, fermentum sed ex ut, pellentesque consectetur mi.",
         3.14159,
         True,
         "up"]]):
    id=f"card-{i}"
    pp(send_receive("query", id=id, name=name, content=content, confidence=confidence, read=read))
    send_receive("mark", id=id, action=ground_truth)

send_receive("finish")
