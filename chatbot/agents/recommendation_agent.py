

import sqlite3
from langchain_groq import ChatGroq

DATABASE_PATH = 'C:/Users/danyn/Documents/car_rental_project/database/rental_car.db'

def recommend_cars_with_groq(preferences, llm):
    """
    Recommends cars dynamically based on multiple user preferences.
    Uses LLM to enhance the recommendation process with intelligent feedback.
    """

    # arrange, not supposed to 
    relevant_preferences = {key: value for key, value in preferences.items() if key not in ["start_date", "end_date"] and value is not None}



    # Build dynamic SQL query
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    query = """
    SELECT Cars.Model, Cars.Brand, Cars.Year, Cars.Color, Cars.PricePerDay, Shop.Location
    FROM Cars
    INNER JOIN Shop ON Cars.ShopID = Shop.ShopID
    WHERE 1=1
    """
    params = []

    # dinamic add conditions based on preferences
    # arrange to add dates (find hwy doe snot work)
    if preferences.get("color"):
        query += " AND LOWER(Cars.Color) = ?"
        params.append(preferences["color"].lower())
    if preferences.get("brand"):
        query += " AND LOWER(Cars.Brand) = ?"
        params.append(preferences["brand"].lower())
    if preferences.get("location"):
        query += " AND LOWER(Shop.Location) = ?"
        params.append(preferences["location"].lower())
    if preferences.get("year"):
        query += " AND Cars.Year = ?"
        params.append(preferences["year"])
    if preferences.get("price"):
        query += " AND Cars.PricePerDay <= ?"
        params.append(preferences["price"])

    print("Constructed Query:", query)
    print("Query Parameters:", params)

    try:
        cursor.execute(query, params)
        results = cursor.fetchall()
    except sqlite3.Error as e:
        return {"message": f"Database error: {e}"}
    finally:
        conn.close()

    #  LLM to format and personalize results
    if results:
        cars = [f"{car[1]} {car[0]} ({car[3]} color) - ${car[4]:.2f}/day in {car[5]}" for car in results]

        prompt = (
            "You are a car rental assistant for a professional car rental company. "
            "Summarize this list of cars in a concise, first-person tone, suitable for a customer:\n" +
            "\n".join(cars)
        )
        messages = [{"role": "system", "content": prompt}]
        response = llm.invoke(messages)
        return {"message": response.content.strip()}

    # If no exact matches are found, suggest fallback cars based on partial preferences
    fallback_query = """
    SELECT Cars.Model, Cars.Brand, Cars.Year, Cars.Color, Cars.PricePerDay, Shop.Location
    FROM Cars
    INNER JOIN Shop ON Cars.ShopID = Shop.ShopID
    WHERE 1=1
    """
    fallback_params = []

    for key, value in relevant_preferences.items():
        if key == "color":
            fallback_query += " AND LOWER(Cars.Color) = ?"
            fallback_params.append(value.lower())
            break
        if key == "brand":
            fallback_query += " AND LOWER(Cars.Brand) = ?"
            fallback_params.append(value.lower())
            break
        if key == "location":
            fallback_query += " AND LOWER(Shop.Location) = ?"
            fallback_params.append(value.lower())
            break

    print("Constructed Fallback Query:", fallback_query)
    print("Fallback Query Parameters:", fallback_params)

    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(fallback_query, fallback_params)
        fallback_results = cursor.fetchall()
    except sqlite3.Error as e:
        return {"message": f"Database error during fallback: {e}"}
    finally:
        conn.close()

    if fallback_results:
        fallback_cars = [f"{car[1]} {car[0]} ({car[3]} color) - ${car[4]:.2f}/day in {car[5]}" for car in fallback_results]
        return {"message": f"Sorry, no cars fully matched your preferences. However, you might like:\n{', '.join(fallback_cars)}."}

    return {"message": "Unfortunately, no cars matched your preferences."}
