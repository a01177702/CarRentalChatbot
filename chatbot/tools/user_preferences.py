# user_preferences

from langchain_core.prompts.chat import SystemMessage, HumanMessage, ChatPromptTemplate
import json




# Initialize user preferences
user_preferences = {
    "color": None,
    "location": None,
    "price_range": None,
    "brand": None,
    "year": None,
    "start_date": None,  #
    "end_date": None     
}




def update_preferences_from_query(query, llm):
    """
    Updates preferences based on a user query.
    Extracts preferences using the LLM and updates the global `user_preferences`.
    """
    # Extract preferences using the LLM
    extracted_preferences = extract_preferences_with_llm(query, llm)
    print("Extracted Preferences:", extracted_preferences)  




    # Update the global 
    for key in user_preferences.keys():
        if key in extracted_preferences:
            user_preferences[key] = extracted_preferences[key]




    return user_preferences


def extract_preferences_with_llm(query, llm):
    """
    Extracts preferences from the user's query using LLM, including start_date and end_date.
    """
    messages = [
        SystemMessage(content=(
            "You are a car rental assistant. Analyze the user's query and extract preferences in JSON format. "
            "Preferences include 'color', 'location', 'price', 'brand', 'year', 'start_date', and 'end_date'. "
            "Ensure the response is valid JSON, e.g., {\"color\": \"blue\", \"start_date\": \"2023-12-01\", \"end_date\": \"2023-12-10\"}."
        )),
        HumanMessage(content=query)
    ]
    prompt = ChatPromptTemplate(messages)
    response = llm.invoke(prompt.format())
    try:
        preferences = json.loads(response.content.strip())
        print("Extracted Preferences:", preferences) 
        return preferences
    except json.JSONDecodeError:
        return user_preferences  # Default fallback
    

    except (json.JSONDecodeError, ValueError) as e:
        # lig the error and return default preferences
        print(f"Error extracting preferences with LLM: {e}")
        return {
            "color": None,
            "location": None,
            "price": None,
            "brand": None,
            "year": None,
            "start_date": None,
            "end_date": None,
        }




def get_preferences():
    """
    Returns the current user preferences.
    """
    return user_preferences
