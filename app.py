from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from datetime import datetime
import json
import os
from dotenv import load_dotenv
load_dotenv()

# Import Dialogflow client library
from google.cloud import dialogflow

app = Flask(__name__)

# Load static responses from JSON
with open('responses.json') as f:
    responses = json.load(f)

# Set Dialogflow configuration: be sure to set DIALOGFLOW_PROJECT_ID in your environment.
DIALOGFLOW_PROJECT_ID = os.environ.get("DIALOGFLOW_PROJECT_ID", "your-dialogflow-project-id")
DIALOGFLOW_LANGUAGE_CODE = 'en-US'

def detect_intent_texts(session_id, text, language_code=DIALOGFLOW_LANGUAGE_CODE):
    """
    Uses Dialogflow to detect intent from a text input.
    Returns the QueryResult object from Dialogflow.
    """
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(DIALOGFLOW_PROJECT_ID, session_id)
    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )
    return response.query_result

# --- Twilio Voice Endpoints ---

@app.route("/voice", methods=['GET', 'POST'])
def voice():
    """
    Initial endpoint for incoming calls via Twilio.
    Plays a welcome message with language selection.
    """
    resp = VoiceResponse()
    gather = Gather(input="speech", action="/handle_inquiry", method="POST", timeout=5)
    gather.say("Hello! Welcome to Wise Customer Support. How can I help you today? You can ask, for example, When will my money arrive?", voice='alice', language='en-US')
    resp.append(gather)
    # If no input is detected, repeat the prompt.
    resp.redirect("/voice")
    return Response(str(resp), mimetype='text/xml')

# @app.route("/process_speech", methods=['GET', 'POST'])
# def process_speech():
#     """
#     Processes the language selection.
#     If English is detected, prompts the user for an inquiry.
#     Otherwise, transfers to a human agent.
#     """
#     resp = VoiceResponse()
#     speech_result = request.values.get('SpeechResult', '').strip().lower()
#     if "english" in speech_result:
#         resp.say("Great! ")
#         gather = Gather(input="speech", action="/handle_inquiry", method="POST", timeout=5)
#         resp.append(gather)
#     else:
#         resp.say("Transferring you to a human agent. Please hold.")
#         resp.hangup()
#     return Response(str(resp), mimetype='text/xml')

@app.route("/handle_inquiry", methods=['GET', 'POST'])
def handle_inquiry():
    """
    Processes the inquiry about money arrival.
    Inserts a weekend note if today is Saturday or Sunday.
    Then prompts the user for feedback.
    """
    resp = VoiceResponse()
    inquiry = request.values.get('SpeechResult', '').strip().lower()
    
    # Determine if today is a weekend (Saturday=5 or Sunday=6)
    today = datetime.today().weekday()
    weekend_note = " Please note, since it's the weekend, transfers may only be processed on the next working day." if today in [5, 6] else ""
    
    base_response = responses.get("when_money_arrives", "")
    final_response = base_response.replace("{weekend_note}", weekend_note)
    
    resp.say(final_response)
    # Gather feedback to process with Dialogflow
    gather = Gather(input="speech", action="/handle_feedback", method="POST", timeout=5)
    resp.append(gather)
    return Response(str(resp), mimetype='text/xml')

@app.route("/handle_feedback", methods=['GET', 'POST'])
def handle_feedback():
    """
    Processes user feedback using Dialogflow for NLU.
    Uses Dialogflow’s detected intent to determine the next response.
    """
    resp = VoiceResponse()
    feedback = request.values.get('SpeechResult', '').strip()
    
    # Use Twilio CallSid (if available) as the Dialogflow session ID; otherwise, default to 'default_session'
    session_id = request.values.get("CallSid", "default_session")
    
    # Call Dialogflow to detect the intent from the user feedback.
    query_result = detect_intent_texts(session_id, feedback)
    
    # Retrieve the intent display name and any fulfillment text from Dialogflow.
    intent_display_name = query_result.intent.display_name.lower()
    fulfillment_text = query_result.fulfillment_text  # Can be used to provide additional details
    
    # Choose a response based on the detected intent.
    if intent_display_name == "satisfied":
        resp.say("I'm glad I could help! Thank you for calling Wise. Have a wonderful day!")
        resp.hangup()
    elif intent_display_name in ["followup", "clarification"]:
        # In a follow-up or clarification intent, use Dialogflow's fulfillment text
        resp.say("I understand. " + fulfillment_text)
        # Re-prompt for further feedback.
        gather = Gather(input="speech", action="/handle_feedback", method="POST", timeout=5)
        resp.append(gather)
    else:
        resp.say("I'm sorry, I didn't quite catch that. " + fulfillment_text)
        gather = Gather(input="speech", action="/handle_feedback", method="POST", timeout=5)
        resp.append(gather)
    return Response(str(resp), mimetype='text/xml')

if __name__ == "__main__":
    app.run(debug=True)
