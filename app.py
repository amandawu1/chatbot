# import requests
# from flask import Flask, request, jsonify
# from llmproxy import generate

# app = Flask(__name__)

# GOOGLE_API_KEY = "AIzaSyDKNUeIRdGOIacjk--fNa2vcs00WHtqHIM"
# SEARCH_ENGINE_ID = "945654d55c45d4da4"

# @app.route('/')
# def hello_world():
#    return jsonify({"text":'Hello from Koyeb - you reached the main page!'})

# def google_search(query):
#     url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={CX}"
#     response = requests.get(url)
#     if response.status_code == 200:
#         results = response.json().get("items", [])
#         summaries = [item["snippet"] for item in results[:5]]
#         return " ".join(summaries)
#     return "No relevant results found."

# @app.route('/query', methods=['POST'])
# def main():
#     data = request.get_json() 

#     # Extract relevant information
#     user = data.get("user_name", "Unknown")
#     message = data.get("text", "")

#     print(data)

#     # Ignore bot messages
#     if data.get("bot") or not message:
#         return jsonify({"status": "ignored"})

#     print(f"Message from {user} : {message}")
    
#     search_summary = google_search(message)

#     # Generate a response using LLMProxy
#     response = generate(
#         model='4o-mini',
#         # system='answer my question and add keywords',
#         system='Summarize the following information and answer the query:',
#         # query= message,
#         query=search_summary,
#         temperature=0.0,
#         lastk=0,
#         session_id='GenericSession'
#     )

#     response_text = response['response']
    
#     # Send response back
#     print(response_text)

#     return jsonify({"text": response_text})
    
# @app.errorhandler(404)
# def page_not_found(e):
#     return "Not Found", 404

# if __name__ == "__main__":
#     app.run()

import os
from flask import Flask, request, jsonify
from llmproxy import generate
import requests

app = Flask(__name__)

API_KEY = os.environ.get("googleApiKey")
CSE_ID = os.environ.get("googleSearchId")

def google_search(query):
    # Performs a Google Custom Search focused on datasets and research papers.
    search_query = (
        f"{query} filetype:pdf OR site:researchgate.net OR site:ncbi.nlm.nih.gov OR site:data.gov "
        "OR site:arxiv.org OR site:worldbank.org OR site:europa.eu OR site:sciencedirect.com OR site:scholar.google.com"
    )
    
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'q': search_query,
        'key': API_KEY,
        'cx': CSE_ID,
        'num': 3  # Limit to top 3 relevant results
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        print(f"Google Search API Error: {response.status_code}, {response.text}")
        return []

    results = response.json().get("items", [])
    
    search_summaries = []
    for item in results:
        title = item.get("title", "No title available")
        snippet = item.get("snippet", "No description available")
        link = item.get("link", "#")
        search_summaries.append(f"**{title}**\n{snippet}\n[🔗 View Paper]({link})\n")

    return search_summaries

@app.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    user = data.get("user_name", "Unknown")
    message = data.get("text", "")

    if data.get("bot") or not message:
        return jsonify({"status": "ignored"})

    try:
        # Step 1: Fetch research papers & datasets
        search_results = google_search(message)
        search_info = "\n".join(search_results) if search_results else ""

        # Step 2: Generate summary response
        query_with_context = f"User query: {message}\n\nResearch Findings:\n{search_info if search_info else 'No relevant research found.'}"
        
        response = generate(
            model='4o-mini',
            system=(
                "You are a Research Assistant AI that specializes in retrieving and summarizing "
                "academic research, datasets, and scientific studies. Your goal is to provide well-cited, "
                "fact-based insights from reputable sources, ensuring that responses reference credible datasets "
                "or peer-reviewed papers whenever possible. Respond as a normal chatbot assistant if the given query does not require citing a source."
            ),
            query=query_with_context,
            temperature=0.0,
            lastk=0,
            session_id='ResearchAssistantSession'
        )

        response_text = response.get('response', "").strip()

        # Build the final response dynamically, only including relevant sections
        response_parts = []
        if response_text and response_text.lower() not in ["hello! how can i assist you today?", "no relevant research found."]:
            response_parts.append(f"**📚 Research Summary:**\n{response_text}")

        if search_info:
            response_parts.append(f"**🔗 Relevant Research Papers & Datasets:**\n{search_info}")

        final_response = "\n\n".join(response_parts) if response_parts else "I'm unable to find relevant research at the moment."

        return jsonify({"text": final_response})

    except Exception as e:
        print(f"Error generating response: {e}")
        return jsonify({"error": "An error occurred while processing your request. Please try again later."}), 500

@app.errorhandler(404)
def page_not_found(e):
    return "Not Found", 404

if __name__ == "__main__":
    app.run()