from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from datetime import datetime
import json
import os
from google.cloud import dialogflow

app = Flask(__name__)

# Load static responses from JSON file
with open('responses_v2.json') as f:
    responses = json.load(f)

# Dialogflow settings
DIALOGFLOW_PROJECT_ID = os.environ.get("DIALOGFLOW_PROJECT_ID", "your-dialogflow-project-id")
DIALOGFLOW_LANGUAGE_CODE = 'en-US'
creds_path = "/etc/secrets/service-account.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path

def detect_intent_texts(session_id, text, language_code=DIALOGFLOW_LANGUAGE_CODE):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(DIALOGFLOW_PROJECT_ID, session_id)
    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(request={"session": session, "query_input": query_input})
    return response.query_result

@app.route("/voice", methods=['GET', 'POST'])
def voice():
    """
    [Start] and [Welcome & Query]
    """
    resp = VoiceResponse()
    gather = Gather(input="speech", action="/handle_inquiry", method="POST", timeout=5)
    gather.say("Welcome to Wise Customer Support. How can I help you today?", voice='alice', language='en-US')
    resp.append(gather)
    resp.redirect("/voice")
    return Response(str(resp), mimetype='text/xml')

@app.route("/handle_inquiry", methods=['GET', 'POST'])
def handle_inquiry():
    """
    [User says Query] & [Identify FAQ Topic]
    Uses Dialogflow to detect the intent of the inquiry. If the intent matches one
    of the FAQ topics, responds with the corresponding answer from responses.json.
    Otherwise, uses Dialogflow's fulfillment text as a fallback.
    """
    resp = VoiceResponse()
    inquiry = request.values.get('SpeechResult', '').strip()
    session_id = request.values.get("CallSid", "default_session")
    query_result = detect_intent_texts(session_id, inquiry)
    intent = query_result.intent.display_name.lower() if query_result.intent.display_name else ""
    
    # Check if the detected intent matches one of our FAQ topics (keys in responses.json)
    if intent in responses:
        reply = responses[intent]
    else:
        # Fallback: use fulfillment text from Dialogflow or a default message
        reply = query_result.fulfillment_text if query_result.fulfillment_text else "I'm sorry, I didn't understand that. Could you please repeat?"
    
    resp.say(reply, voice='alice', language='en-US')
    
    # [User Feedback] prompt
    gather = Gather(input="speech", action="/handle_feedback", method="POST", timeout=5)
    gather.params = {"LastResponse": reply}  # Store last response
    resp.say("How does that sound?", voice='alice', language='en-US')
    resp.append(gather)
    
    return Response(str(resp), mimetype='text/xml')

@app.route("/handle_feedback", methods=['GET', 'POST'])
def handle_feedback():
    """
    [NLU Intent Extraction] for feedback.
    Processes feedback using Dialogflow to detect if the user is satisfied, wants followup,
    or is unclear. Ends the call or re-prompts accordingly.
    """
    resp = VoiceResponse()
    feedback = request.values.get('SpeechResult', '').strip()
    session_id = request.values.get("CallSid", "default_session")
    query_result = detect_intent_texts(session_id, feedback)
    intent = query_result.intent.display_name.lower() if query_result.intent.display_name else ""
    
    # Retrieve last response from previous inquiry
    last_response = request.values.get("LastResponse", "I'm sorry, I didn't understand that.")

    if intent == "satisfied":
        resp.say(responses.get("satisfied"), voice='alice', language='en-US')
        resp.hangup()
    elif intent == "followup":
        resp.say(responses.get("followup"), voice='alice', language='en-US')
        resp.hangup() # placeholder for human agent transfer
    elif intent == "unclear":
        # Repeat the last response before asking again
        resp.say(f"{last_response}. Could you please clarify?", voice='alice', language='en-US')
        gather = Gather(input="speech", action="/handle_feedback", method="POST", timeout=5)
        gather.params = {"LastResponse": last_response}  # Keep last response stored
        resp.append(gather)
    else:
        resp.say("I'm sorry, I didn't quite catch that. Could you please repeat or clarify?", voice='alice', language='en-US')
        gather = Gather(input="speech", action="/handle_feedback", method="POST", timeout=5)
        gather.params = {"LastResponse": last_response}  # Keep last response stored
        resp.append(gather)
    
    return Response(str(resp), mimetype='text/xml')

if __name__ == "__main__":
    app.run(debug=True)
