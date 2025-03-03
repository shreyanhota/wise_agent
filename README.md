# Wise Voice Agent

Contact : Shreyan Hota (shreyanhota@gmail.com)

# Files
- app_v2.py - Flask app, receives requests from Twilio API and handles the conversation flow, along with Dialogflow for NLU (intent recognition).
- responses_v2.json - Helper json for Twilio, defining agent reponses according to Dialogflow-recognized intents
- requirements.txt - Python packages to be installed

## Note : 
- The frontend is deployed on a separate web service (https://wise-agent-frontend.onrender.com/). In case it is inaccessible, please drop a mail to shreyanhota@gmail.com or reach out to me at +91 9777256250 and I will respool the servers.
- Twilio API is in Trial Mode, once you receive call from the agent, please press any key to start the agent.

## Overview
Wise Voice Agent is a voice-based customer support solution built with Twilio's Voice API, Dialogflow, Python Flask, and deployed on Render. It calls the provided number, processes user queries through natural language understanding, and responds with pre-defined FAQ answers stored in a JSON file. The agent is designed to streamline customer support by quickly providing answers to frequently asked questions about money transfers.

## Architecture
- Twilio Voice API: Handles incoming calls, text-to-speech responses, and gathers caller input.
- Dialogflow: Processes and extracts intents from the user's spoken queries.
- Python Flask: Serves as the backend application framework that integrates Twilio and Dialogflow.
- JSON Configuration: Stores FAQ responses mapped to specific intents.
- Render Deployment: The entire application is hosted on Render, using Gunicorn as the production server.

## Call Handling:
When a call is received, the agent greets the user and prompts for a query. The call flow is managed using Twilio’s Gather functionality.

## Intent Detection
The spoken query is sent to Dialogflow, which analyzes it and returns the corresponding intent. If the intent matches one of the FAQ topics, the system retrieves a summarized answer from the JSON file.

## Response & Feedback
The agent delivers the answer and then asks, "Would you like to know more, or did that answer your query?" The feedback is then processed—if the response corresponds to one of the FAQ topics, the conversation loops back to the inquiry phase.

## Fallback & Escalation
If the intent is not recognized or the answer is unclear, the agent requests clarification or routes the call to a human agent as needed.

## Option Listing
A specific intent allows users to ask for the list of available FAQ options, which are then read out as a complete list.

## Deployment
The project is deployed as a single web service on Render. 

## Future Improvements and Next Steps
- Context and Memory:
  Improve User Experience by checking current date and modifying responses based on current day being weekend or weekday.

- Automatic Account Information Retrieval:
  Based on registered mobile number, extract information to provide context to responses.

- Enhanced Intent Training:
  Improve the training phrases in Dialogflow to capture a wider range of user queries and to increase the accuracy of intent detection.

- Expand FAQ Topics:
  Add more detailed FAQ topics based on user feedback and support analytics to further enrich the knowledge base.

- Logging and Monitoring:
  Implement robust logging and monitoring mechanisms to track interactions, detect errors, and analyze performance metrics.

- Testing and Validation:
  Develop unit tests and integration tests to ensure reliability. Incorporate input validation and error handling to improve system robustness.

- User Experience Enhancements:
  Refine voice interactions and consider adding multi-language support for a more personalized experience. Improve the dialogue flow and clarity of responses.

- Human Agent Integration:
  Enhance the process for routing calls to human agents when the automated system cannot resolve a query effectively.

- Analytics Dashboard:
  Build an analytics dashboard to monitor common queries, track system performance, and inform future improvements.
