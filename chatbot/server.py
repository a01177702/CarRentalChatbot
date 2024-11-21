from flask import Flask, request, jsonify
from flask_cors import CORS
from agents.manager_agent import process_input  # For routing queries to the appropriate agent
from tools.user_preferences import update_preferences_from_query, get_preferences
from agents.recommendation_agent import recommend_cars_with_groq
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"))

app = Flask(__name__)
CORS(app)  # cross origin

@app.route('/chat', methods=['POST'])
def chat():
    """
    Handles chat queries from the user and routes them to the appropriate agent.
    """
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        # Update user preferences
        preferences = update_preferences_from_query(user_message, llm)

        # Process query and route to the appropriate agent
        response = process_input(user_message)

        #   chatbot response and preferences for debugging
        return jsonify({
            "response": response,
            "preferences": preferences
        })
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/preferences', methods=['GET'])
def get_user_preferences():
    """
    Returns the current user preferences.
    """
    try:
        preferences = get_preferences()
        return jsonify(preferences)
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
