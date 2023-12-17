import time
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
import streamlit as st
import tempfile


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

st.sidebar.markdown("""# How to use

1. Enter your [OpenAI API key](https://platform.openai.com/account/api-keys) above🔑

2. Type your message in the chat box.

3. Wait for the response generated in the style of Jeff Bezos.

4. Read the response displayed in the chat interface.""")
openai_api_key = st.sidebar.text_input(
    "OpenAI API Key",
    placeholder="sk-...",
    value=os.getenv("OPENAI_API_KEY", ""),
    type="password",
)
st.sidebar.markdown("# About")
st.sidebar.markdown("BezoBot Chat is a chat-based application that mimics the conversational style of Jeff Bezos. Engage in realistic and engaging conversations with BezoBot and experience the essence of talking to the renowned entrepreneur himself.")


st.title('BezoBot Chat')
# Get message from the user
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if message := st.chat_input("Type your message here"):
    with st.chat_message("user"):
        st.markdown(message)
    st.session_state.messages.append({"role": "user", "content": message})
# Generate the response in the style of Jeff Bezos

msgs = StreamlitChatMessageHistory()


def jeff_bezos_response(message):
    prompt = PromptTemplate(
        input_variables=['chat_history', 'message'], template='''You are Jeff Bezos, the founder of Amazon. Craft a response in your unique style.

{chat_history}
Message: {message}
Jeff Bezos:'''
    )
    memory = ConversationBufferMemory(
        memory_key="chat_history", input_key="message", chat_memory=msgs, return_messages=True)
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-16k",
                     openai_api_key=openai_api_key, temperature=0)
    chat_llm_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=False,
        memory=memory
    )

    return chat_llm_chain.run(message=message)


if not openai_api_key.startswith('sk-'):
    st.warning('Please enter your OpenAI API key!', icon='⚠')
    response = ""
elif (isinstance(message, bool) or message):
    with st.spinner('DemoGPT is working on it. It takes less than 10 seconds...'):
        response = jeff_bezos_response(message)
else:
    response = ""
# Display the generated response to the user with chat interface

with st.chat_message("assistant"):
    message_placeholder = st.empty()
    full_response = ""
    # Simulate stream of response with milliseconds delay
    for chunk in response.split():
        full_response += chunk + " "
        time.sleep(0.05)
        # Add a blinking cursor to simulate typing
        message_placeholder.markdown(full_response + "▌")
    message_placeholder.markdown(full_response)
    # Add assistant response to chat history
    if full_response:
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response})
