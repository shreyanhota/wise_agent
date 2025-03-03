from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from datetime import datetime
import json
import os
from google.cloud import dialogflow

app = Flask(__name__)

with open('responses_v2.json') as f:
    responses = json.load(f)

DIALOGFLOW_PROJECT_ID = os.environ.get("DIALOGFLOW_PROJECT_ID")
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
    resp = VoiceResponse()
    gather = Gather(input="speech", action="/handle_inquiry", method="POST", timeout=5)
    gather.say("Welcome to Wise Customer Support. How can I help you today? You can ask me for a list of options.", voice='alice', language='en-US')
    resp.append(gather)
    resp.redirect("/voice")
    return Response(str(resp), mimetype='text/xml')

@app.route("/handle_inquiry", methods=['GET', 'POST'])
def handle_inquiry():
    resp = VoiceResponse()
    inquiry = request.values.get('SpeechResult', '').strip()
    session_id = request.values.get("CallSid", "default_session")
    query_result = detect_intent_texts(session_id, inquiry)
    intent = query_result.intent.display_name.lower() if query_result.intent.display_name else ""
    
    reply = responses[intent]
    faq_intents = [
        "check_transfer_status", 
        "money_arrival", 
        "transfer_complete_but_money_pending", 
        "transfer_delay_reasons", 
        "proof_of_payment", 
        "banking_partner_reference"
    ]
    if intent in faq_intents:
        reply = responses[intent]
        resp.say(reply, voice='alice', language='en-US')
        resp.say("Would you like to know more, or did that answer your query?", voice='alice', language='en-US')
    else:
        reply = responses[intent]
        resp.say(reply, voice='alice', language='en-US')

    gather = Gather(input="speech", action="/handle_feedback", method="POST", timeout=5)
    gather.params = {"LastResponse": reply}
    resp.append(gather)
    
    return Response(str(resp), mimetype='text/xml')

@app.route("/handle_feedback", methods=['GET', 'POST'])
def handle_feedback():
    resp = VoiceResponse()
    feedback = request.values.get('SpeechResult', '').strip()
    session_id = request.values.get("CallSid", "default_session")
    query_result = detect_intent_texts(session_id, feedback)
    intent = query_result.intent.display_name.lower() if query_result.intent.display_name else ""

    faq_intents = [
        "check_transfer_status", 
        "money_arrival", 
        "transfer_complete_but_money_pending", 
        "transfer_delay_reasons", 
        "proof_of_payment", 
        "banking_partner_reference",
        "check_options"
    ]

    if intent in faq_intents:
        request.values = request.values.copy()
        request.values["SpeechResult"] = feedback
        return handle_inquiry()

    if intent == "satisfied":
        resp.say(responses.get("satisfied"), voice='alice', language='en-US')
        resp.hangup()
    elif intent == "followup":
        resp.say(responses.get("followup"), voice='alice', language='en-US')
        resp.hangup() # placeholder for call routing to human agent
    elif intent == "unclear":
        last_response = request.values.get("LastResponse", "I'm sorry, I didn't understand that.")
        resp.say(f"{last_response}. Was that audible?", voice='alice', language='en-US')
        gather = Gather(input="speech", action="/handle_feedback", method="POST", timeout=5)
        gather.params = {"LastResponse": last_response}
        resp.append(gather)
    else:
        resp.say("I'm sorry, I may not be able to answer that, connecting you to a human agent.", voice='alice', language='en-US')
        resp.hangup() # placeholder for call routing to human agent
    
    return Response(str(resp), mimetype='text/xml')

if __name__ == "__main__":
    app.run(debug=True)
