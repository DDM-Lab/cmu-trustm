import requests

requests.post("http://localhost:8000/start",
              json={"name": "How to mumble a fuchsia stack snorkel"})

print(requests.post("http://localhost:8000/query",
                    json={"id": "card-1",
                          "name": "Fuchsia Snorkels Stack Brilliantly",
                          "content": "Lorem ipsum dolor sit amet, consectetur fuchsia adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim snorkel veniam, quis stack nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non snorkel proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
                          "confidence": 3.14159}).json())

requests.post("http://localhost:8000/mark", json={"id": "card-1", "action": "up"})
