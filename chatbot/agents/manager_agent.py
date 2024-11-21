
from nodes.price import handle_price_query
from nodes.color import get_cars_by_color_with_groq
from nodes.availability import check_availability
from agents.recommendation_agent import recommend_cars_with_groq
from agents.booking_agent import handle_booking_intent, reset_booking_session
from nodes.location import get_cars_by_location_with_groq
from nodes.year import get_cars_by_year_with_groq
from nodes.brand import get_models_by_brand_with_groq
from langchain_groq import ChatGroq
from langchain_core.prompts.chat import SystemMessage, HumanMessage, ChatPromptTemplate
from dotenv import load_dotenv
from tools.helpers import parse_natural_language_date, get_current_year
from datetime import datetime
import os
import json

# Global session memory for booking state
session_memory = {
    "active_booking": False,
    "preferences": {}
}



load_dotenv()
llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"))

def process_input(query):
    """
    Processes the user query by detecting intent and preferences,
    then routes the query to the appropriate agent or node.
    """
    global session_memory

    # Detect intent and extract preferences
    intent_data = detect_intent_with_llm(query)
    intent = extract_intent_from_llm_response(intent_data)
    preferences = extract_preferences_with_llm(query, llm)

    print(f"Detected Intent: {intent}")
    print(f"Extracted Preferences: {preferences}")

    # Handle active booking session
    if session_memory["active_booking"]:
        print("Booking session active. Updating preferences...")
        for key, value in preferences.items():
            if value:
                session_memory["preferences"][key] = value
        return handle_booking_intent(query, session_memory["preferences"], llm)

    # If booking intent, start a booking session
    if intent == "booking":
        session_memory["active_booking"] = True
        session_memory["preferences"] = preferences
        return handle_booking_intent(query, preferences, llm)

    # Count non-date preferences for recommendation logic
    non_date_preferences = {key: value for key, value in preferences.items() if key not in ["start_date", "end_date"] and value is not None}
    if len(non_date_preferences) >= 2:
        return recommend_cars_with_groq(preferences, llm)

    # Route based on intent
    if intent == "availability_query":
        return check_availability(preferences)
    elif intent == "price_query":
        return handle_price_query(query, llm)
    elif intent == "color_query":
        return get_cars_by_color_with_groq(query, llm)
    elif intent == "location_query":
        return get_cars_by_location_with_groq(query, llm)
    elif intent == "year_query":
        return get_cars_by_year_with_groq(query, llm)
    elif intent == "brand_query":
        return get_models_by_brand_with_groq(query, llm)

    # Fallback message
    return {"message": "I'm here to help! You can ask for car prices, availability, or recommendations."}

def detect_intent_with_llm(query):
    """
    Detects the user's intent using the LLM by sending the query
    as part of a structured prompt that clarifies the intent categories.
    """
    messages = [
        SystemMessage(content=(
            "You are a car rental assistant. Identify the user's intent and relevant details from their query. "
            "Possible intents include booking a car, checking car availability (based on month, date, or time frame), "
            "finding car prices, exploring options by color, finding cars by location, seeking recommendations, "
            "or inquiring about car brands and models. "
            "A query mentioning more than one preference (e.g., color, brand, and location) is likely a recommendation_request. "
            "Respond with only one of these intents: availability_query, price_query, color_query, "
            "location_query, year_query, recommendation_request, 'booking', or brand_query."
        )),
        HumanMessage(content=query)
    ]
    prompt = ChatPromptTemplate(messages)
    prompt_text = prompt.format()
    response = llm.invoke(prompt_text)

    print(f"Raw Intent Response: {response.content.strip()}")  #
    return response.content.strip()

def extract_intent_from_llm_response(llm_response):
    """
    Extracts the intent from the LLM's response based on exact matches.
    """
    valid_intents = {
        "availability_query",
        "price_query",
        "color_query",
        "location_query",
        "year_query",
        "recommendation_request",
        "brand_query",
        "booking"
    }

    intent = llm_response.lower().strip()
    return intent if intent in valid_intents else "general_query"

def extract_preferences_with_llm(query, llm):
    """
    Extracts preferences from the user's query using LLM.
    Handles natural language dates and ensures the current year is added if missing.
    """
    messages = [
        SystemMessage(content=(
            "You are a car rental assistant. Analyze the user's query and extract preferences in JSON format. "
            "Preferences can include 'color', 'location', 'price', 'brand', 'year', 'start_date', or 'end_date'. "
            "Respond in JSON format, e.g., {\"color\": \"blue\", \"brand\": \"audi\", \"location\": null, \"year\": 2020, \"price\": 100, \"start_date\": \"December 1\", \"end_date\": \"December 10\"}."
        )),
        HumanMessage(content=query)
    ]
    prompt = ChatPromptTemplate(messages)
    prompt_text = prompt.format()

    try:
        response = llm.invoke(prompt_text)
        preferences = json.loads(response.content.strip())
        print(f"Raw Preferences from LLM: {preferences}")

        current_year = get_current_year()

        if preferences.get("start_date"):
            preferences["start_date"] = parse_natural_language_date(preferences["start_date"], current_year)
        if preferences.get("end_date"):
            preferences["end_date"] = parse_natural_language_date(preferences["end_date"], current_year)

        return preferences

    except json.JSONDecodeError as e:
        print(f"Error extracting preferences with LLM: {e}")
        return {"color": None, "location": None, "price": None, "brand": None, "year": None, "start_date": None, "end_date": None}
