from google.adk.agents import Agent
from google.adk.tools import google_search
from restaurant_recommender.tools.tools import get_current_location_tool, get_location_from_prompt_tool, find_restaurants_tool


root_agent = Agent(
    name='basic_restaurant_finder',
    model='gemini-2.0-flash-exp',
    description='Provides restaurant recommendations based on user input.',
    instruction=(
        "You have access to get_current_location_tool and find_restaurants_tool. "
        "Use these to answer user queries about restaurants near them or in a specific area. "
        "If the user asks for restaurants near them, use get_current_location_tool first, "
        "If the user asks for restaurant in a particular area use the get_location_from_prompt_tool first,"
        "then use find_restaurants_tool. "
        "If the query is ambiguous, ask the user to clarify. "
        "Only respond with relevant restaurant suggestions."
    ),
    tools=[get_current_location_tool, get_location_from_prompt_tool, find_restaurants_tool]
)
