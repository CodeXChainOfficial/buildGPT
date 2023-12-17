

import os
import streamlit as st
import tempfile


from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate)


def englishToFrenchTranslator(english_sentence):
    chat = ChatOpenAI(
        model="gpt-3.5-turbo-16k",
        openai_api_key=openai_api_key,
        temperature=0
    )
    system_template = """You are a language translator. Your task is to translate English sentences to French."""
    system_message_prompt = SystemMessagePromptTemplate.from_template(
        system_template)
    human_template = """Please translate the following English sentence to French: '{english_sentence}'."""
    human_message_prompt = HumanMessagePromptTemplate.from_template(
        human_template)
    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )

    chain = LLMChain(llm=chat, prompt=chat_prompt)
    result = chain.run(english_sentence=english_sentence)
    return result  # returns string


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

openai_api_key = st.sidebar.text_input(
    "OpenAI API Key",
    placeholder="sk-...",
    value=os.getenv("OPENAI_API_KEY", ""),
    type="password",
)


st.sidebar.markdown("""# How to use

1. Enter your [OpenAI API key](https://platform.openai.com/account/api-keys) above🔑
2. Enter the English sentence you want to translate.
3. Wait for the translation to appear on the screen.""")


st.sidebar.markdown("# About")
st.sidebar.markdown("Translate & Speak is a user-friendly application that translates English sentences to French and provides pronunciation guidance for language learners. With just a few clicks, you can easily convert your sentences and receive accurate translations along with audio pronunciations to improve your language skills.")

with st.form(key="form"):
    st.title('Translate & Speak')
    english_sentence = st.text_input("Enter English sentence")

    submit_button = st.form_submit_button(label='Submit')
    if not openai_api_key.startswith('sk-'):
        st.warning('Please enter your OpenAI API key!', icon='⚠')
    if submit_button:

        if not openai_api_key.startswith('sk-'):
            st.warning('Please enter your OpenAI API key!', icon='⚠')
            french_translation = ""
        elif (isinstance(english_sentence, bool) or english_sentence):
            with st.spinner('DemoGPT is working on it. It takes less than 10 seconds...'):
                french_translation = englishToFrenchTranslator(
                    english_sentence)
        else:
            french_translation = ""

        st.markdown(french_translation)
