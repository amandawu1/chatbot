import requests
from flask import Flask, request, jsonify
from llmproxy import generate
import os

app = Flask(__name__)

GOOGLE_API_KEY = os.environ.get("googleSearchAPI")
SEARCH_ENGINE_ID = os.environ.get("searchID")

@app.route('/')
def hello_world():
   return jsonify({"text":'Hello from Koyeb - you reached the main page!'})

def google_search(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}"
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json().get("items", [])
        summaries = [item["snippet"] for item in results[:5]]
        return " ".join(summaries)
    return "No relevant results found."

@app.route('/query', methods=['POST'])
def main():
    data = request.get_json() 

    # Extract relevant information
    user = data.get("user_name", "Unknown")
    message = data.get("text", "")

    print(data)

    # Ignore bot messages
    if data.get("bot") or not message:
        return jsonify({"status": "ignored"})

    print(f"Message from {user} : {message}")
    
    search_summary = google_search(message)

    # Generate a response using LLMProxy
    response = generate(
        model='4o-mini',
        system='Consolidate the following information without making it sound like a summary. Cite sources as links. Please also break up text into bullet points as appropriate.',
        query=search_summary,
        temperature=0.0,
        lastk=0,
        session_id='GenericSession' #take userID into account to create separate sessionIDs for multiple simultaneous users
    )

    response_text = response['response']
    
    # Send response back
    print(response_text)

    return jsonify({"text": response_text})
    
@app.errorhandler(404)
def page_not_found(e):
    return "Not Found", 404

if __name__ == "__main__":
    app.run()