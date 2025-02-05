from langgraph.graph import StateGraph, END
from tools import GoogleCalendarTool
from langchain_community.llms import OpenAI
from dotenv import load_dotenv
import os

credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
calendar_tool = GoogleCalendarTool(credentials)

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

if openai_api_key is None:
    raise ValueError("OPENAI_API_KEY environment variable not set.")

llm = OpenAI(
    temperature=0,
    model_name="gpt-3.5-turbo",
    openai_api_key=openai_api_key,
)

graph = StateGraph()


@graph.node
def plan(state):
    user_request = state.get("user_request")

    prompt = f"""
    Extract the following information from the user request:
    - summary(event title)
    - start (ISO 8601 datetime string)
    - end (ISO 8601 datetime string)
    - attendees (list of email addresses)

    User Request: {user_request}

    Output the Information as a JSON object. 
    """
    llm_output = llm(prompt)

    try:
        import json
        booking_details = json.loads(llm_output)
        booking_details.setdefault("summary", "Appointment")
        booking_details.setdefault("attendees", [])
        return {"booking_details":booking_details}
    except json.JSONDecodeError:
        return {"booking_details": None, "error": "Invalid JSON in LLM output"}
    

@graph.node
def check_avaliability(state):
    booking_details = state.get("booking_details")
    if booking_details is None:
        return {"availability": "error", "booking_details": None, "error": state.get("error")}
    availability = calendar_tool.check_avaliability(booking_details)
    return {"availability": availability, "booking_details": booking_details}

@graph.node
def confirmation(state):
    event = state.get("event")
    return {"response": f"Appointment Booked Successfully: {event}"}

@graph.nodes
def handle_error(state):
    error_message = state.get("error_message")
    return {"response": f"An Error: {error_message}"}

graph.add_edge("plan", "check_avaliability")

graph.add_edge("check_avaliability", "book_event", condition = lambda state: state.get("availability") == "availability")
graph.add_edge("check_availability", "plan", condition = lambda state: state.get("availability") != "availability" and state.get("availability") != "error")
graph.add_edge("check_availability", "handle_error", condition = lambda state: state.get("availability") != "error")

graph.add_edge("plan", "handle_error", condition=lambda state:state.get("booking_details") is None)

graph.add_edge("book_event", "confirmation")

graph.set_entry_point("plan")

agent = graph.create_agent()
langgraph_agent = agent

