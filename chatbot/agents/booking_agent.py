
import sqlite3
from langchain_groq import ChatGroq

DATABASE_PATH = 'C:/Users/danyn/Documents/car_rental_project/database/rental_car.db'

# Memory to store session state and preferences
session_memory = {
    "active_booking": False,
    "preferences": {}
}

# General: add dates (ask)

def handle_booking_intent(query, preferences, llm):
    """
    Handles the car booking process.
    Uses LLM to guide the conversation and format responses.
    """
    global session_memory

    # Start booking session if not active
    if not session_memory["active_booking"]:
        session_memory["active_booking"] = True
        session_memory["preferences"] = preferences.copy()
        return {
            "message": "Great! Let's start your booking. What are your preferences for the car? (e.g., color, brand, location, date range)."
        }

    # Update session preferences with new details from the query
    for key, value in preferences.items():
        if value:
            session_memory["preferences"][key] = value

    # If no preferences are provided yet, ask for them
    if not any(session_memory["preferences"].values()):
        return {
            "message": "I still need more details to help you. Could you share your preferences for the car? (e.g., color, brand, location, etc.)"
        }

    # Fetch cars matching the current preferences
    cars = query_cars_with_preferences(session_memory["preferences"])

    # If a single car is found, finalize the booking
    if len(cars) == 1:
        selected_car = cars[0]
        reset_booking_session()  # Reset session after booking

        #  LLM for a confirmation message
        car_details = {
            "brand": selected_car[1],
            "model": selected_car[0],
            "year": selected_car[2],
            "color": selected_car[3],
            "price": f"{selected_car[4]:.2f}",
            "location": selected_car[5],
        }
        confirmation_prompt = (
            f"You are a car rental assistant. Based on the user's preferences, suggest this car as a booking option. Dont say hello or goodbye"
            f"Include the details below in a friendly and professional tone, but concisely and clarify that this is an option, not a final confirmation:\n"
            f"{car_details['brand']} {car_details['model']} ({car_details['year']}, {car_details['color']}) - "
            f"${car_details['price']}/day located in {car_details['location']}.\n\n"
            "End the message by letting the user know you're available to help with recommendations, more bookings, or any questions. "
        )
        messages = [{"role": "system", "content": confirmation_prompt}]
        response = llm.invoke(messages)

        return {
            "message": response.content.strip(),
            "car_details": car_details,  # Pass car details for the frontend
        }

    # If multiple cars are found, ask the user to narrow down preferences
    if len(cars) > 1:
        car_options = [
            f"{idx + 1}. {car[1]} {car[0]} ({car[3]} color, {car[2]} year) - ${car[4]:.2f}/day in {car[5]}"
            for idx, car in enumerate(cars)
        ]
        return {
            "message": "I found multiple cars matching your preferences. Please choose one from the options below:\n" + "\n".join(car_options),
        }

    # if no matches are found, suggest fallback options
    fallback_cars = fetch_fallback_cars(preferences)
    if fallback_cars:
        fallback_options = [
            f"{idx + 1}. {car[1]} {car[0]} ({car[3]} color) - ${car[4]:.2f}/day in {car[5]}"
            for idx, car in enumerate(fallback_cars)
        ]
        return {
            "message": "No exact matches were found for your preferences, but you might be interested in the following cars:\n"
            + "\n".join(fallback_options)
        }

    # If no fallback matches are available, reset session
    reset_booking_session()
    return {
        "message": "Unfortunately, I couldn't find any cars matching your preferences. Please try adjusting your criteria or starting over."
    }


def reset_booking_session():
    """
    Resets the booking session state.
    """
    global session_memory
    session_memory["active_booking"] = False
    session_memory["preferences"] = {}


def query_cars_with_preferences(preferences):
    """
    Queries the database for cars matching user preferences, eliminating duplicates.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    query = """
    SELECT DISTINCT Cars.Model, Cars.Brand, Cars.Year, Cars.Color, Cars.PricePerDay, Shop.Location
    FROM Cars
    INNER JOIN Shop ON Cars.ShopID = Shop.ShopID
    INNER JOIN CarAvailability ON Cars.CarID = CarAvailability.CarID
    WHERE 1=1
    """
    params = []

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
    if preferences.get("start_date") and preferences.get("end_date"):
        query += " AND CarAvailability.StartDate <= ? AND CarAvailability.EndDate >= ?"
        params.append(preferences["end_date"])
        params.append(preferences["start_date"])

    print("Executing Query:", query)
    print("Query Parameters:", params)

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    # Remove doiuble rows if they still exist after query execution
    unique_results = list(set(results))
    return unique_results


def fetch_fallback_cars(preferences):
    """
    Fetches fallback cars matching at least one of the user's preferences.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    query = """
    SELECT Cars.Model, Cars.Brand, Cars.Year, Cars.Color, Cars.PricePerDay, Shop.Location
    FROM Cars
    INNER JOIN Shop ON Cars.ShopID = Shop.ShopID
    WHERE 1=1
    """
    params = []

    # Match on any single preference
    if preferences.get("color"):
        query += " AND LOWER(Cars.Color) = ?"
        params.append(preferences["color"].lower())
    elif preferences.get("brand"):
        query += " AND LOWER(Cars.Brand) = ?"
        params.append(preferences["brand"].lower())
    elif preferences.get("location"):
        query += " AND LOWER(Shop.Location) = ?"
        params.append(preferences["location"].lower())

    print("Executing Fallback Query:", query)
    print("Fallback Query Parameters:", params)

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results
