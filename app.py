import InvokeLambda as agenthelper
import streamlit as st
import json
import time
from log_setup import logger
from lxml import etree
from html import unescape
import re
# Streamlit page configuration
st.set_page_config(page_title="Chatbot", page_icon="💬", layout="wide")


if "history" not in st.session_state:
    st.session_state.history = []
    st.session_state.case = ""
    logger.info('New History Created !!')


st.sidebar.title("**Sample Queries:**")
sample_queries = [
    "Is there a victim?",
    "Give me summary",
    "What is the type of crime the defendant was arrested for?",
    "Is the defendant on any form of Criminal Release/Probation?",
    "Does the defendant have prior arrests?",
    "How many arrests?",
    "How many convictions?",
   " Is there a Domestic Violence act involved?",
    "Was a firearm used?",
    "Was anyone threatened?",
    "Were drugs used?",
    "Is there a field test?",
    "What is the defendant’s domesticity?",
    "Did the defendant attempt to avoid arrest?",
]
for query in sample_queries:
    st.sidebar.markdown(query)

#Displaying all the previous messages
for message in st.session_state.history:
    with st.chat_message("user"):
        st.markdown(message["question"])
    with st.chat_message("assistant"):
        st.markdown(message["answer"])
    
#random ID generator
st.session_state.session_id = "ChatBot-Session"

# Display a text box for input
if prompt := st.chat_input("Ex.- Enter the Query"):

    with st.chat_message("user"):
        st.markdown(prompt)
    full_response = ""

    match = re.search(r'\bcase\s+([^:]+)', prompt, re.IGNORECASE)
    if match:
        case_name = match.group(1).strip()  # Remove leading/trailing whitespace
        st.session_state.case = case_name
        response_text = "Case Opened !!"
        print("print session in if:", st.session_state.case)
        the_response = response_text
    elif st.session_state.case:
        case_name = st.session_state.case
        print("print session in elif:", st.session_state.case)
        temp_prompt = f"{prompt} in {case_name}"
        # Prepare and invoke the lambda function since this is not a new case
        event = {"question": temp_prompt}
    
        #Invoking Agent
        response = agenthelper.lambda_handler(event, None)
        responseJson = json.loads(response['body'])
        the_response = responseJson['response']
        logger.debug(f'response: {the_response}')
    else:
            the_response = 'No case name found in the query.'
            print("print session in else:", st.session_state.case)
            
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        # Adding a small delay while displaying to make it like streaming
        for chunk in the_response.split("\\n"):  # Splitting on literal \n to handle new lines correctly
            full_response += unescape(chunk) + " "  # Handle XML entities and append space for proper formatting
            time.sleep(0.1)
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(full_response.strip() + "▌")

    # Save the history with unescaped newlines for future correct display
    st.session_state.history.append({"question": prompt, "answer": full_response.strip()})