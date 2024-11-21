

import sqlite3
from datetime import datetime
from tools.helpers import parse_natural_language_date, get_current_year

DATABASE_PATH = 'C:/Users/danyn/Documents/car_rental_project/database/rental_car.db'

def check_availability(preferences):
    """
    Handles availability queries using the database for date ranges.
    """
    # Extract raw dates from preferences
    raw_start_date = preferences.get("start_date")
    raw_end_date = preferences.get("end_date")

    print(f"Raw Start Date: {raw_start_date}, Raw End Date: {raw_end_date}")

    # Use current year if not explicitly provided
    current_year = get_current_year()

    try:
        # Handle missing dates
        if not raw_start_date or not raw_end_date:
            return {"message": "Please specify valid start and end dates in YYYY-MM-DD format or natural language."}

        # Parse the dates
        start_date = parse_natural_language_date(raw_start_date, current_year)
        end_date = parse_natural_language_date(raw_end_date, current_year)

        print(f"Parsed Start Date: {start_date}, Parsed End Date: {end_date}")

        if not start_date or not end_date:
            return {"message": "Please specify valid start and end dates in YYYY-MM-DD format or natural language."}

    except Exception as e:
        return {"message": f"Error processing dates: {str(e)}"}

    # Query the database
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        sql_query = """
        SELECT Cars.Model, Cars.Brand, Cars.Year, Cars.Color, Cars.PricePerDay, Shop.Location
        FROM Cars
        INNER JOIN Shop ON Cars.ShopID = Shop.ShopID
        INNER JOIN CarAvailability ON Cars.CarID = CarAvailability.CarID
        WHERE CarAvailability.StartDate <= ? AND CarAvailability.EndDate >= ?
        """
        print("Executing SQL Query:", sql_query)
        print("Query Parameters:", (end_date, start_date))

        # Execute the query with parsed dates
        cursor.execute(sql_query, (end_date, start_date))
        results = cursor.fetchall()

        print("Query Results:", results)

    except sqlite3.Error as e:
        return {"message": f"Database error: {e}"}

    finally:
        conn.close()

    # Format and return the results
    if results:
        cars = [
            f"{car[1]} {car[0]} ({car[2]}, {car[3]} color) - ${car[4]:.2f}/day in {car[5]}"
            for car in results
        ]
        return {"message": "Here are the available cars:\n" + "\n".join(cars)}

    return {"message": f"No cars are available from {start_date} to {end_date}."}
