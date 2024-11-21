#helpers.py
import sqlite3
from datetime import datetime
from dateutil import parser  
import re
from dateutil.parser import parse
import json

DATABASE_PATH = 'C:/Users/danyn/Documents/car_rental_project/database/rental_car.db'

def detect_car_brand_in_query(query):
    """Detects car brand in the query based on database records."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT Brand FROM Cars")
        brands = [row[0].lower() for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()

    for brand in brands:
        if brand in query.lower():
            return brand.capitalize()
    return None

def detect_car_model_in_query(query):
    """Detects car model in the query based on database records."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        # Fetch all models
        cursor.execute("SELECT DISTINCT Model FROM Cars")
        models = [row[0].lower() for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Database error in detect_car_model_in_query: {e}")
        return None
    finally:
        conn.close()

    query_lower = query.lower()

    # Check for exact or partial matches
    for model in models:
        if model in query_lower:
            return model.capitalize() 
    return None

def extract_date_from_query(query):
    """Extracts start and end dates from the user's query."""
    date_range_pattern = r"from (\w+ \d{1,2}) to (\w+ \d{1,2})"
    match = re.search(date_range_pattern, query, re.IGNORECASE)

    if match:
        try:
            start_date = parser.parse(match.group(1)).date() 
            end_date = parser.parse(match.group(2)).date()
            return start_date, end_date
        except ValueError:
            return None, None

    single_date_pattern = r"on (\w+ \d{1,2})"
    match = re.search(single_date_pattern, query, re.IGNORECASE)
    if match:
        try:
            single_date = parser.parse(match.group(1)).date()  
            return single_date, None
        except ValueError:
            return None, None

    return None, None

def parse_natural_language_date(date_string, default_year):
    """
    Translates date strings into YYYY-MM-DD format.
    Preserves explicitly provided years.
    Adds the current year for natural language dates without a year.
    """
    try:
        # Check if the date string is already in  YYYY-MM-DD format
        if re.match(r"^\d{4}-\d{2}-\d{2}$", date_string):
            return date_string

        #  natural language dates
        parsed_date = parser.parse(date_string, fuzzy=True, default=datetime(default_year, 1, 1))

        #  if the parsed date defaulted to the defaultyear because no year was provided
        if parsed_date.year == default_year and re.search(r"\d{4}", date_string):
            # If a year is explicitly mentioned in the input, retain it
            return parsed_date.strftime("%Y-%m-%d")

        return parsed_date.strftime("%Y-%m-%d")
    except (ValueError, TypeError) as e:
        print(f"Error parsing date: {e}")
        return None



def get_current_year():
    """
    Returns the current year dynamically.
    """
    current_year = datetime.now().year
    print(f"Current Year: {current_year}")  
    return current_year
