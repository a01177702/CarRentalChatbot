# brand.py
import sqlite3
from langchain_groq import ChatGroq
from langchain_core.prompts.chat import SystemMessage, HumanMessage, ChatPromptTemplate

DATABASE_PATH = 'C:/Users/danyn/Documents/car_rental_project/database/rental_car.db'

def get_models_by_brand_with_groq(query, llm):
    """
    Handles brand-based queries using the database and LLM for enriched responses.
    """
    # Detect the brand from the  query
    brand = detect_brand_in_query(query)
    if not brand:
        return enrich_response_with_llm("Please specify a valid brand in your query. For example, BMW, Tesla, or Toyota.", llm)

    #  car models from the specified brand
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT Model, Year, Color FROM Cars WHERE Brand = ?", (brand,))
        results = cursor.fetchall()
    except sqlite3.Error as e:
        return f"Database error: {e}"
    finally:
        conn.close()

    # Format and return the response
    if results:
        cars = [f"{car[0]} ({car[1]}, {car[2]} color)" for car in results]
        return enrich_response_with_llm(f"Cars by {brand}: {', '.join(cars)}.", llm)
    return enrich_response_with_llm(f"No cars available by {brand}.", llm)

def detect_brand_in_query(query):
    """
    Detects a brand in the user's query by matching it against database values.
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT Brand FROM Cars")
        brands = [row[0] for row in cursor.fetchall()] 
    except sqlite3.Error as e:
        return None
    finally:
        conn.close()

    # Caseinsensitive matching
    query_lower = query.lower()
    for brand in brands:
        if brand.lower() in query_lower:
            return brand  # Return the original case from the database
    return None

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
