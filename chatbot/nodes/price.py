# price.py
import sqlite3
from langchain_groq import ChatGroq
from langchain_core.prompts.chat import SystemMessage, HumanMessage, ChatPromptTemplate
from dotenv import load_dotenv
import os


load_dotenv()
llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"))

DATABASE_PATH = 'C:/Users/danyn/Documents/car_rental_project/database/rental_car.db'

def handle_price_query(query, llm):
    """
    Handles price-related queries using the database and LLM.
    """
    # Detect price range and filter type from query
    price_threshold, filter_type = detect_price_in_query(query)
    
    if price_threshold is not None:
        if filter_type == "below":
            return get_cars_below_or_equal_price(price_threshold, llm)
        elif filter_type == "above":
            return get_cars_above_price(price_threshold, llm)
        elif filter_type == "costs":
            return get_cars_with_exact_price(price_threshold, llm)

    car_brand = detect_car_brand_in_query(query)
    car_model = detect_car_model_in_query(query)

    if car_model:
        return get_price_by_model(car_model, llm)
    elif car_brand:
        return get_prices_by_brand(car_brand, llm)
    else:
        return enrich_response_with_llm(
            "Please specify a car brand, model, or price range to provide price information.", llm
        )

def get_cars_below_or_equal_price(price_threshold, llm):
    """Fetches cars with a daily price below or equal to the given threshold."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        sql_query = "SELECT Model, Brand, Year, PricePerDay FROM Cars WHERE PricePerDay <= ?"
        cursor.execute(sql_query, (price_threshold,))
        results = cursor.fetchall()
    except sqlite3.Error as e:
        return f"Database error: {e}"
    finally:
        conn.close()

    if results:
        cars = [f"{car[0]} ({car[1]}, {car[2]}) - ${car[3]:.2f} per day" for car in results]
        base_response = f"Here are the cars available under or equal to ${price_threshold:.2f} per day:\n" + "\n".join(cars)
        return enrich_response_with_llm(base_response, llm)
    return enrich_response_with_llm(f"No cars are available under or equal to ${price_threshold:.2f} per day.", llm)

def get_cars_above_price(price_threshold, llm):
    """Fetches cars with a daily price above the given threshold."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        sql_query = "SELECT Model, Brand, Year, PricePerDay FROM Cars WHERE PricePerDay > ?"
        cursor.execute(sql_query, (price_threshold,))
        results = cursor.fetchall()
    except sqlite3.Error as e:
        return f"Database error: {e}"
    finally:
        conn.close()

    if results:
        cars = [f"{car[0]} ({car[1]}, {car[2]}) - ${car[3]:.2f} per day" for car in results]
        base_response = f"Here are the cars available above ${price_threshold:.2f} per day:\n" + "\n".join(cars)
        return enrich_response_with_llm(base_response, llm)
    return enrich_response_with_llm(f"No cars are available above ${price_threshold:.2f} per day.", llm)

def get_cars_with_exact_price(price_threshold, llm):
    """Fetches cars with a daily price exactly equal to the given threshold."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        sql_query = "SELECT Model, Brand, Year, PricePerDay FROM Cars WHERE PricePerDay = ?"
        cursor.execute(sql_query, (price_threshold,))
        results = cursor.fetchall()
    except sqlite3.Error as e:
        return f"Database error: {e}"
    finally:
        conn.close()

    if results:
        cars = [f"{car[0]} ({car[1]}, {car[2]}) - ${car[3]:.2f} per day" for car in results]
        base_response = f"Here are the cars available for exactly ${price_threshold:.2f} per day:\n" + "\n".join(cars)
        return enrich_response_with_llm(base_response, llm)
    return enrich_response_with_llm(f"No cars are available for exactly ${price_threshold:.2f} per day.", llm)

def get_price_by_model(car_model, llm):
    """Fetches price for a specific car model and uses LLM to enrich the response."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT PricePerDay, PriceIfMonth FROM Cars WHERE LOWER(Model) = ?", (car_model.lower(),))
        result = cursor.fetchone()
    except sqlite3.Error as e:
        return f"Database error: {e}"
    finally:
        conn.close()

    if result:
        daily_price, monthly_price = result
        base_response = f"The price for {car_model.capitalize()} is ${daily_price:.2f} per day or ${monthly_price:.2f} per month."
        return enrich_response_with_llm(base_response, llm)
    return enrich_response_with_llm(f"Price information for {car_model.capitalize()} is not available.", llm)

def get_prices_by_brand(car_brand, llm):
    """Fetches prices for all models of a given brand and uses LLM to enrich the response."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT Model, PricePerDay, PriceIfMonth FROM Cars WHERE LOWER(Brand) = ?", (car_brand.lower(),))
        results = cursor.fetchall()
    except sqlite3.Error as e:
        return f"Database error: {e}"
    finally:
        conn.close()

    if results:
        cars = [f"{car[0]}: ${car[1]:.2f}/day, ${car[2]:.2f}/month" for car in results]
        base_response = f"Here are the prices for {car_brand.capitalize()} models:\n" + "\n".join(cars)
        return enrich_response_with_llm(base_response, llm)
    return enrich_response_with_llm(f"No pricing information available for {car_brand.capitalize()}.", llm)

def detect_price_in_query(query):
    """
    Detects a price threshold and filter type (below, above, exact) in the user's query.
    Examples: 'under 70', 'below 100', 'cheaper than 50', 'above 100', 'for 70'.
    """
    import re
    # Match for phrases 
    match = re.search(r'\b(under|below|less than|cheaper than|above|for)\s(\d+)', query.lower())
    if match:
        filter_type = match.group(1)
        price = float(match.group(2))
        if filter_type in ["under", "below", "less than", "cheaper than"]:
            return price, "below"
        elif filter_type == "above":
            return price, "above"
        elif filter_type == "for":
            return price, "exact"
    return None, None

def detect_car_model_in_query(query):
    """Detects car model in the query based on database records."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT Model FROM Cars")
        models = [row[0].lower() for row in cursor.fetchall()]
    except sqlite3.Error as e:
        return None
    finally:
        conn.close()

    for model in models:
        if model in query.lower():
            return model.capitalize()
    return None

def detect_car_brand_in_query(query):
    """Detects car brand in the query based on database records."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT Brand FROM Cars")
        brands = [row[0].lower() for row in cursor.fetchall()]
    except sqlite3.Error as e:
        return None
    finally:
        conn.close()

    for brand in brands:
        if brand in query.lower():
            return brand.capitalize()
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
