# location.py
import sqlite3
from langchain_groq import ChatGroq
from langchain_core.prompts.chat import SystemMessage, HumanMessage, ChatPromptTemplate
from dotenv import load_dotenv
import os


load_dotenv()
llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"))

DATABASE_PATH = 'C:/Users/danyn/Documents/car_rental_project/database/rental_car.db'

def get_cars_by_location_with_groq(query, llm):
    """
    Handles location-based queries using the database and LLM for enriched responses.
    """
    location, available_locations = detect_location_in_query(query)
    if not location:
        # Respond with available locations if the queried location is not found
        locations_list = ', '.join([loc.capitalize() for loc in available_locations])
        return enrich_response_with_llm(
            f"We currently don't have any shops in the specified location. "
            f"Our available shops are in: {locations_list}.", llm
        )

    # Query th for cars available at the specified location
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        sql_query = """
            SELECT Cars.Model, Cars.Brand, Cars.Year, Cars.Color
            FROM Cars
            JOIN Shop ON Cars.ShopID = Shop.ShopID
            WHERE LOWER(Shop.Location) = ?
        """
        cursor.execute(sql_query, (location.lower(),))  #  caseinsensitive matching
        results = cursor.fetchall()
    except sqlite3.Error as e:
        return f"Database error: {e}"
    finally:
        conn.close()

    # Format and return the response
    if results:
        cars = [f"{car[0]} ({car[1]}, {car[2]}) - {car[3]} color" for car in results]
        return enrich_response_with_llm(f"Cars available in {location.capitalize()}: {', '.join(cars)}.", llm)
    return enrich_response_with_llm(f"No cars are available in {location.capitalize()}.", llm)

def detect_location_in_query(query):
    """
    Detects a location in the user's query by matching it against database values.
    Returns the detected location and the list of all available locations.
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT LOWER(Location) FROM Shop")
        locations = [row[0] for row in cursor.fetchall()]  
    except sqlite3.Error as e:
        return None, []
    finally:
        conn.close()

    query_lower = query.lower()
    for location in locations:
        if location in query_lower:
            return location.capitalize(), locations  # Return found location and all available locations
    return None, locations  

def enrich_response_with_llm(base_response, llm):
    """
    Enhances the base response using the LLM for a conversational tone.
    """
    messages = [
        SystemMessage(content="You are a car rental assistant. Respond to the user's query with concise details. If you give several options do not list the options with numbers, just give each option as a sentence. And be supportive if needed something else."),
        HumanMessage(content=base_response)
    ]
    prompt = ChatPromptTemplate(messages)
    prompt_text = prompt.format()
    response = llm.invoke(prompt_text)
    return response.content
