# year.py
import sqlite3
from langchain_groq import ChatGroq
from langchain_core.prompts.chat import SystemMessage, HumanMessage, ChatPromptTemplate
from dotenv import load_dotenv
import os
from datetime import datetime
from word2number import w2n  #  to convert words to numbers


load_dotenv()
llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"))

DATABASE_PATH = 'C:/Users/danyn/Documents/car_rental_project/database/rental_car.db'

def get_cars_by_year_with_groq(query, llm):
    """
    Handles year-based queries using the database and LLM for enriched responses.
    """
    year = detect_year_in_query(query)
    if not year:
        return enrich_response_with_llm(
            "Please specify a valid year in your query. For example, 'cars from 2022' or 'cars from four years ago.'", llm
        )

    #   database for cars from the specified year
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        sql_query = "SELECT Model, Brand, Color FROM Cars WHERE Year = ?"
        print(f"Executing query for year: {year}") 
        cursor.execute(sql_query, (year,))
        results = cursor.fetchall()
        print(f"Query Results: {results}") 
    except sqlite3.Error as e:
        return f"Database error: {e}"
    finally:
        conn.close()

    # Format and return the response
    if results:
        cars = [f"{car[0]} ({car[1]}, {car[2]} color)" for car in results]
        return enrich_response_with_llm(f"Cars from {year}: {', '.join(cars)}.", llm)
    return enrich_response_with_llm(f"No cars are available from {year}.", llm)

def detect_year_in_query(query):
    """
    Detects a year in the user's query, including relative years (e.g., 'last year', 'four years ago').
    """
    import re

    # Match explicit years 
    match = re.search(r'\b(19|20)\d{2}\b', query)
    if match:
        year = int(match.group())
        print(f"Detected explicit year: {year}")
        return year

    # Handle relative years in words or numbers 
    relative_match = re.search(r'(\d+|[a-z]+)\s+years?\s+ago', query.lower())
    if relative_match:
        try:
            # Convert word to number if necessary
            years_ago = relative_match.group(1)
            if not years_ago.isdigit():
                years_ago = w2n.word_to_num(years_ago)  
            current_year = datetime.now().year
            detected_year = current_year - int(years_ago)
            print(f"Detected relative year: {detected_year}")
            return detected_year
        except ValueError as e:
            print(f"Error detecting relative year: {e}")
            return None

    # Handle specific phrases
    current_year = datetime.now().year
    if "last year" in query.lower():
        print(f"Detected phrase 'last year': {current_year - 1}")
        return current_year - 1
    if "next year" in query.lower():
        print(f"Detected phrase 'next year': {current_year + 1}")
        return current_year + 1
    if "this year" in query.lower():
        print(f"Detected phrase 'this year': {current_year}")
        return current_year

    print("No valid year detected.")
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
