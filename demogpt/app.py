import logging
import os
import signal
import sys
import traceback
import subprocess
import streamlit as st
import streamlit.components.v1 as components
from streamlit.components.v1 import html
import socket

current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file_path)
parent_directory = os.path.dirname(current_directory)
grandparent_directory = os.path.dirname(parent_directory)
sys.path.append(grandparent_directory)

from model import DemoGPT
from utils import runStreamlit

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception as e:
    logging.error("dotenv import error but no needed")


def generate_response(txt):
    """
    Generate response using the LangChainCoder.

    Args:
        txt (str): The input text.

    Yields:
        dict: A dictionary containing response information.
    """
    for data in agent(txt):
        yield data


def initCode():
    if "code" not in st.session_state:
        st.session_state["code"] = ""
        st.session_state.edit_mode = False


def save_code_to_file(code, filename='generated_file.py'):
    with open(filename, 'w') as file:
        file.write(code)
    st.success(f'Code saved to {filename}')
    return filename

def run_code_file(filename):
    try:
        # This will set up the subprocess to run the streamlit app, capturing the output.
        # The `check` argument if set to True will raise a CalledProcessError if the command returns a non-zero exit status.
        # Note that if running this command succeeds, it will not terminate until the streamlit app is closed.
        result = subprocess.run(['streamlit', 'run', filename], capture_output=True, text=True, check=True)
        stdout = result.stdout
        stderr = result.stderr
        return stdout, stderr
    except subprocess.CalledProcessError as e:
        # Handle errors during subprocess run.
        st.error(f'An error occurred: {e}')
        return e.stdout, e.stderr


def get_open_app_script(ip_address, port):
    return f"""
    <script>
    window.open('http://{ip_address}:{port}/', '_blank');
    </script>
    """
# Page title
title = "🧩 DemoGPT"

st.set_page_config(page_title=title)
    
st.title(title)


initCode()

# Text input

openai_api_key = "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"
openai_api_base = "https://api.openai.com/v1"
models = (
    "gpt-3.5-turbo-0613",
    "gpt-3.5-turbo-0301",
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-16k",
    "gpt-3.5-turbo-16k-0613",
    "gpt-4",
    "gpt-4-0314",
    "gpt-4-0613",
)

model_name = st.sidebar.selectbox("Model", models)

overview = st.text_area(
    "Explain your LLM-based application idea *",
    placeholder="Type your application idea here",
    height=100,
    help="""## Example prompts
* Character Clone: Want an app that converses like Jeff Bezos? Prompt - "A chat-based application that talks like Jeff Bezos."
* Language Mastery: Need help in learning French? Prompt - "An application that translates English sentences to French and provides pronunciation guidance for learners. 
* Content Generation: Looking to generate content? Prompt - "A system that can write ready to share Medium article from website. The resulting Medium article should be creative and interesting and written in a markdown format."
    """,
)

features = st.text_input(
    "List all specific features desired for your app (comma seperated)",
    placeholder="Document interpretation, question answering, ...",
    help="Please provide a comprehensive list of specific features and functionalities you envision in your application, ensuring each element supports your overall objectives and user needs.(comma seperated)"
    )

if overview and features:
    demo_idea = f"Overview:{overview}\nFeatures:{features}"
elif overview:
    demo_idea = overview
else:
    demo_idea = ""

def progressBar(percentage, bar=None):
    if bar:
        bar.progress(percentage)
    else:
        return st.progress(percentage)


if "pid" not in st.session_state:
    st.session_state["pid"] = -1

if "done" not in st.session_state:
    st.session_state["done"] = False

with st.form("a", clear_on_submit=True):
    submitted = st.form_submit_button("Submit")


def kill():
    if st.session_state["pid"] != -1:
        logging.info(f"Terminating the previous applicaton ...")
        try:
            os.kill(st.session_state["pid"], signal.SIGTERM)
        except Exception as e:
            pass
        st.session_state["pid"] = -1


if submitted:
    if not demo_idea:
        st.warning("Please enter your demo idea", icon="⚠️")
        st.stop()

    st.session_state.messages = []
    if not openai_api_key:
        st.warning("Please enter your OpenAI API Key!", icon="⚠️")
    elif demo_idea:
        bar = progressBar(0)
        st.session_state.container = st.container()
        try:  # This line must be aligned with its corresponding except block
            agent = DemoGPT(openai_api_key=openai_api_key, openai_api_base=openai_api_base)
            agent.setModel(model_name)
            for data in generate_response(demo_idea):
                done = data.get("done", False)
                failed = data.get("failed", False)
                message = data.get("message", "")
                st.session_state["message"] = message
                stage = data.get("stage", "stage")
                code = data.get("code", "")
                progressBar(data["percentage"], bar)

                st.session_state["done"] = done
                st.session_state["failed"] = failed
                st.session_state["message"] = message

                if done or failed:
                    st.session_state.code = code
                    break

                st.info(message, icon="🧩")
                st.session_state.messages.append(message)
        except Exception as e:  # This line must be at the same indentation level as the try block
            error_message = traceback.format_exc()
            st.error(f"An error occurred: {error_message}")
            logging.error(error_message)
            st.session_state["done"] = True
            st.session_state["failed"] = True

elif "messages" in st.session_state:
    for message in st.session_state.messages:
        st.info(message, icon="🧩")

if 'filename' not in st.session_state:
    st.session_state.filename = ""

if st.session_state.done and not st.session_state.edit_mode:
    st.success(st.session_state.message)
    with st.expander("Code", expanded=True):
        code_empty = st.empty()
        code_empty.code(st.session_state.code)
        
        if st.button("Edit"):
            st.session_state.edit_mode = True  # Enter edit mode
            st.experimental_rerun()
    
           # Handle the save file operation
    if st.button('Save File'):
        st.session_state.filename = save_code_to_file(st.session_state.code)
        st.success(f'File saved as {st.session_state.filename}')

    # Before running the file, ensure the filename is set
    if st.button('Run File'):
        if not st.session_state.filename:
            st.error("No file has been saved yet. Please save the file before running.")
        else:
            stdout, stderr = run_code_file(st.session_state.filename)
            if stdout:
                st.code(stdout, language='bash')
            if stderr:
                st.error(stderr)
            
            # After running the code, extract the correct IP address and port
            # Get the local system's hostname
            hostname = socket.gethostname()
            # Then retrieve the local IP address
            ip_address = socket.gethostbyname(hostname)
            port = "8503"  # Set the correct port that Streamlit runs on
            
            # Create the HTML for the link to the running app
            st.markdown(f'<a href="http://{ip_address}:{port}/" target="_blank">Open the running app</a>', unsafe_allow_html=True)
      

# Download button logic ...
st.download_button(
    label="Download Code",
    data=st.session_state.code,
    file_name='generated_code.py',
    mime='text/plain'
)

    
if st.session_state.get("failed", False):
    with st.form("fail"):
        st.warning(st.session_state["message"])
        email = st.text_input("Email", placeholder="example@example.com")
        email_submit = st.form_submit_button("Send")
    if email_submit:
        st.success(
            "🌟 Thank you for entrusting us with your vision! We're on it and will ping you the moment your app is ready to launch. Stay tuned for a stellar update soon!"
        )
