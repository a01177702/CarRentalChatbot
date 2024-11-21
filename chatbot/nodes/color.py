# color.py
import sqlite3
from langchain_groq import ChatGroq
from langchain_core.prompts.chat import SystemMessage, HumanMessage, ChatPromptTemplate

DATABASE_PATH = 'C:/Users/danyn/Documents/car_rental_project/database/rental_car.db'

def get_cars_by_color_with_groq(query, llm):
    """
    Handles color-based queries using the database and LLM for enriched responses.
    """
    color = detect_color_in_query(query)
    if not color:
        return enrich_response_with_llm("Please specify a color in your query.", llm)

    #  database for cars with the specified color
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT Model, Brand, Year, PricePerDay FROM Cars WHERE Color = ?", (color.capitalize(),))
    results = cursor.fetchall()
    conn.close()

    if results:
        cars = [f"{car[0]} ({car[1]}, {car[2]}) - ${car[3]:.2f} per day" for car in results]
        base_response = f"Here are the cars available in {color.capitalize()}:\n" + "\n".join(cars)
        return enrich_response_with_llm(base_response, llm)
    return enrich_response_with_llm(f"No cars available in {color.capitalize()}.", llm)

def detect_color_in_query(query):
    """
    Detects a color in the user's query by matching it against database values.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT Color FROM Cars")
    colors = [row[0].lower() for row in cursor.fetchall()]
    conn.close()

    for color in colors:
        if color in query.lower():
            return color
    return None

def enrich_response_with_llm(base_response, llm):
    """
    Enhances the base response using the LLM for a more conversational tone.
    """
    messages = [
        SystemMessage(content="You are a car rental assistant. Respond to the user's query with concise details. Do not give extra information if not needed. If you give several options do not list the options with numbers, just give each option as a sentence. And be supportive if needed something else."),
        HumanMessage(content=base_response)
    ]
    prompt = ChatPromptTemplate(messages)
    prompt_text = prompt.format()
    response = llm.invoke(prompt_text)
    return response.content
