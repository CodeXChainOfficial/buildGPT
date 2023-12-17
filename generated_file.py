

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


def pronunciationGuide(french_translation):
    chat = ChatOpenAI(
        model="gpt-3.5-turbo-16k",
        openai_api_key=openai_api_key,
        temperature=0
    )
    system_template = """You are a language expert providing pronunciation guidance for French translations."""
    system_message_prompt = SystemMessagePromptTemplate.from_template(
        system_template)
    human_template = """Please provide the pronunciation guidance for the French translation: '{french_translation}'."""
    human_message_prompt = HumanMessagePromptTemplate.from_template(
        human_template)
    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )

    chain = LLMChain(llm=chat, prompt=chat_prompt)
    result = chain.run(french_translation=french_translation)
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

3. Wait for the translation to be generated.

4. Once the translation is ready, the French translation will be displayed.

5. If you need pronunciation guidance for the French translation, wait for it to be generated.

6. Once the pronunciation guidance is ready, it will be displayed to you.""")


st.sidebar.markdown("# About")
st.sidebar.markdown("Français Made Easy is an application that makes learning French effortless. It translates English sentences to French and provides pronunciation guidance, helping learners improve their language skills with ease.")

with st.form(key="form"):
    st.title('Français Made Easy')
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

        if not openai_api_key.startswith('sk-'):
            st.warning('Please enter your OpenAI API key!', icon='⚠')
            pronunciation_guidance = ""
        elif (isinstance(french_translation, bool) or french_translation):
            with st.spinner('DemoGPT is working on it. It takes less than 10 seconds...'):
                pronunciation_guidance = pronunciationGuide(french_translation)
        else:
            pronunciation_guidance = ""

        st.markdown(pronunciation_guidance)
