import os
import streamlit as st
import tempfile

import shutil
from langchain.document_loaders import *


from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain


def load_video(youtube_link):
    loader = YoutubeLoader.from_youtube_url(youtube_link, add_video_info=False)
    docs = loader.load()
    return docs


def generate_recap(video_doc):
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k",
                     openai_api_key=openai_api_key)
    chain = load_summarize_chain(llm, chain_type="stuff")
    with st.spinner('DemoGPT is working on it. It might take 5-10 seconds...'):
        return chain.run(video_doc)


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

openai_api_key = st.sidebar.text_input(
    "OpenAI API Key",
    placeholder="sk-...",
    value=os.getenv("OPENAI_API_KEY", ""),
    type="password",
)


st.sidebar.markdown("""'''
# How to use

1. Enter your [OpenAI API key](https://platform.openai.com/account/api-keys) above🔑
2. Provide the YouTube link in the designated input field.
3. Wait for the application to load the YouTube video as a document.
4. The application will then generate a recap from the document.
5. Once the recap is ready, it will be displayed to you.
'''""")


st.sidebar.markdown("# About")
st.sidebar.markdown("RehashTube is a web application that generates concise recaps of any YouTube video. Simply input the YouTube link and get a quick summary of the video's content. Perfect for those who want to save time or catch up on content quickly.")

with st.form(key="form"):
    st.title('RehashTube')
    youtube_link = st.text_input("Enter YouTube link")

    submit_button = st.form_submit_button(label='Submit')
    if not openai_api_key.startswith('sk-'):
        st.warning('Please enter your OpenAI API key!', icon='⚠')
    if submit_button:

        if youtube_link:
            video_doc = load_video(youtube_link)
        else:
            video_doc = ''

        if not openai_api_key.startswith('sk-'):
            st.warning('Please enter your OpenAI API key!', icon='⚠')
            recap_text = ""
        elif video_doc:
            recap_text = generate_recap(video_doc)
        else:
            variable = ""

        st.markdown(recap_text)
