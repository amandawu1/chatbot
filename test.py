import requests

response_main = requests.get("https://lengthy-kerrill-test443-a8de268b.koyeb.app/")
print('Web Application Response:\n', response_main.text, '\n\n')


data = {"text":"tell me about tufts"}
response_llmproxy = requests.post("https://lengthy-kerrill-test443-a8de268b.koyeb.app//query", json=data)
print('LLMProxy Response:\n', response_llmproxy.text)
