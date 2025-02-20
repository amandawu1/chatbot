import requests

response_main = requests.get("https://dizzy-eran-test443-99cdf70c.koyeb.app/")
print('Web Application Response:\n', response_main.text, '\n\n')


data = {"text":"tell me about tufts"}
response_llmproxy = requests.post("https://dizzy-eran-test443-99cdf70c.koyeb.app//query", json=data)
print('LLMProxy Response:\n', response_llmproxy.text)
