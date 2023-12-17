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

st.sidebar.markdown("""'''
# How to use

1. Enter your [OpenAI API key](https://platform.openai.com/account/api-keys) above🔑

2. Input your message or query related to blockchain, web3, NFT, or smart contracts in the chat interface.

3. Click on the 'Send' button or press 'Enter' to submit your message.

4. Wait for a moment while the system analyzes your message and generates a response.

5. The response will be displayed in the chat interface. You can continue the conversation by sending more messages.
'''""")
openai_api_key = st.sidebar.text_input(
    "OpenAI API Key",
    placeholder="sk-...",
    value=os.getenv("OPENAI_API_KEY", ""),
    type="password",
)
st.sidebar.markdown("# About")
st.sidebar.markdown("ChainBot: Sarcasm Inc is a Telegram chatbot designed to provide comprehensive answers about blockchain and web3. It also allows users to deploy NFTs and smart contracts using natural chain. This bot is your go-to resource for all things related to blockchain technology.")


st.title('ChainBot: Sarcasm Inc')
# Get message from the user
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if message := st.chat_input("Type your message here"):
    with st.chat_message("user"):
        st.markdown(message)
    st.session_state.messages.append({"role": "user", "content": message})
# Analyze the message and generate a response related to blockchain, web3, nft, and smart contract

msgs = StreamlitChatMessageHistory()


def blockchain_related_response(message):
    prompt = PromptTemplate(
        input_variables=['chat_history', 'message'], template='''You are a chatbot having a conversation with a human. Analyze the message and generate a response related to blockchain, web3, nft, and smart contract.

{chat_history}
Human: {message}
Chatbot:'''
    )
    memory = ConversationBufferMemory(
        memory_key="chat_history", input_key="message", chat_memory=msgs, return_messages=True)
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-16k",
                     openai_api_key=openai_api_key, temperature=0.7)
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
        response = blockchain_related_response(message)
else:
    response = ""
# Display the generated response to the user

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
