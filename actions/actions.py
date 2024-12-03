from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import sqlite3

class CollectDetails(Action):
    
    def name(self) -> str:
        return "collect_details"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:
        
        # Retrieve slots for event and seats
        event_name = tracker.get_slot("event")
        seats = tracker.get_slot("seats")
        
        # Connect to the database to fetch available events
        conn = sqlite3.connect('instance/bookticket.db')
        cursor = conn.cursor()
        cursor.execute("SELECT ename FROM events")
        events = cursor.fetchall()
        event_list = [event[0].strip().lower() for event in events]
        conn.close()

        # Check if event is valid
        if not event_name or event_name.strip().lower() not in event_list:
            # Event not provided or not found in list, prompt with available events
            buttons = [{"title": event[0], "payload": f'/book_ticket{{"event":"{event[0]}"}}'} for event in events[:5]]
            dispatcher.utter_message(text="Please select an event from the list:", buttons=buttons)
            return [SlotSet("event", None)]
        
        # Check if seat count is provided
        if not seats:
            # Seats not provided, prompt for seat count
            seat_buttons = [{"title": str(i), "payload": f'/book_ticket{{"seats":"{i}"}}'} for i in range(1, 7)]
            dispatcher.utter_message(text="How many seats would you like to book?", buttons=seat_buttons)
            return []
        
        # Validate seat count (optional)
        try:
            seat_count = int(seats)
            if seat_count < 1 or seat_count > 6:
                dispatcher.utter_message(text="Please select between 1 and 6 seats.")
                return [SlotSet("seats", None)]
        except ValueError:
            dispatcher.utter_message(text="Invalid number of seats. Please select a valid number.")
            return [SlotSet("seats", None)]
        
        # Confirmation for booking
        dispatcher.utter_message(
            text=f"Do you want to confirm your booking for '{event_name}' with {seats} seats?",
            buttons=[
                {"title": "Yes", "payload": "/affirm"},
                {"title": "No", "payload": "/deny"}
            ]
        )
        return [SlotSet("event", event_name), SlotSet("seats", seats)]
