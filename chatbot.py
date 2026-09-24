from google import genai # gemini's SDK
from config import GEMINI_API_KEY #API key that config.py already loaded
from prompts import SYSTEM_PROMPT
import time

# Check that the API key exists
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set. Please check your .env file.")

"""AUTHENTICATION + CREATE/USE A CLIENT"""
# connect Python to Gemini API (Client- object provided by Google)
"""Create a Gemini API client and
authenticate it using this API key"""
client = genai.Client(api_key=GEMINI_API_KEY)

"""
The flow is now: .env > config.py > GEMINI_API_KEY > chatbot.py
"""

previous_interaction_id = None # to connect one turn to the next

class ConversationManager:
    def __init__(self): # initializes the convo history as an empty list
        self.messages = [] # messages belonging to this particular convo object

    # adding message to convo history (self.messages)
    # add_message()- method
    def add_message(self, role, content):
        self.messages.append({
            "role": role,
            "content": content
        })

    # only the last few (upto -max_messages) messages
    # if -4, then last 4 messages
    def trim_history(self, max_messages):
        self.messages = self.messages[-max_messages:]

    # clears/empties the entire conversation history
    # no deletion
    def clear_history(self):
        self.messages.clear()

    def get_summary(self):
        message_count = len(self.messages)

        total_characters = sum(
            len(message["content"]) for message in self.messages
        )

        approximate_tokens = round(total_characters / 4)  # Rough estimate: 1 token ≈ 4 chars

        return message_count, approximate_tokens

    # gives the convo history when called
    # hides the implementation details of how the messages are stored (encapsulation)
    def get_history(self):
        return self.messages

conversation = ConversationManager() # object creation (conversation)

def clear_conversation():
    global previous_interaction_id

    conversation.clear_history()
    previous_interaction_id = None

def ask_gemini(question): # reusability- not repeating the same API call code for every question

    # handles empty/whitespaced input
    # checks if input is empty
    if not question.strip(): # removes whitespace from the beginning and end
        print("Please enter a valid question.")
        return ""

    # adding previous_interaction_id = None here would
    # create/reset the local variable every time
    global previous_interaction_id # to modify the variable that was created outside the function

     # store user's prompt as soon as the app receives it
    conversation.add_message("user", question)

    time.sleep(5)
    print("Thinking....")

    for attempt in range(3):
        try:
            """SEND A QUESTION/REQUEST TO GEMINI API"""
            # using the client object
            # creating 'streaming interaction' with the model

            # tells it which previous interaction to continue from
            # asks it to return the response as a stream
            stream = client.interactions.create( # sends req to Gemini
                model="gemini-3.6-flash", # tells Gemini which model to use
                input=f"{SYSTEM_PROMPT}\n\n{question}", # question to ask
                previous_interaction_id=previous_interaction_id,
                stream=True
            )

            answer = ""
            interaction_completed = False # to check if the interaction is completed

            # event- object that represents a single event/chunk in the streaming interaction
            # # saves the interaction ID so the next turn can continue from this interaction
            for event in stream:
                if event.event_type == "interaction.created":
                    pass # do nothing here, so continue with the other conditions

                elif event.event_type == "step.delta":
                    if event.delta.type == "text":
                        print(event.delta.text, end="", flush=True)
                        answer += event.delta.text # build the complete ans to add it to convo history
                
                # if interaction is completed
                elif event.event_type == "interaction.completed":
                    interaction_completed = True
                    previous_interaction_id = event.interaction.id # saves interaction ID

                # if interaction fails
                # gemini's message isn't then stored anymore
                # doesn't reach the 'break' statement
                # leaves this inner loop and try block, and then goes to except block
                elif event.event_type == "error":
                    raise RuntimeError(str(event.error))

            break # if everything succeeds, break out of the retry (outer) loop. needs to be inside for this reason

        except Exception as e:
            error_message = str(e) # convert error object (e) into ordinary text

            if "rate_limit_exceeded" in error_message.lower():
                print("\nYour daily Gemini API request limit reached (20 requests per day on Free Tier). Please try again after the quota resets. Visit https://aistudio.google.com/rate-limit?timeRange=last-28-days&project=peak-scope-413403 to check your quota.")
                return ""

            # transient errors (rate limit/service unavailable/high demand model)
            elif (
                "429" in error_message
                or "503" in error_message
                or "high demand" in error_message.lower()
            ):
                if attempt < 1: # retry if attempt is available
                    wait_time = 2 ** attempt # giving increasingly more time (exponential) to recover
                    print(f"\nTemporary error. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time) # pauses for that time and continues with the loop
                else:
                    print(f"\nSomething went wrong: {e}")
                    return "" # no proper ans to store if API fails
            
            # permanent errors (invalid input/API key)
            else:
                print(f"\nSomething went wrong: {e}")
                return ""

    if not interaction_completed:
        print("\nThe response did not complete.")
        return ""

    conversation.add_message("assistant", answer)

    return answer