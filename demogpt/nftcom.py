import os
import streamlit as st
import tempfile


from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate)


def nftCommissionCalculator(nft, service, referral_code, commission_percentage):
    chat = ChatOpenAI(
        model="gpt-3.5-turbo-16k",
        openai_api_key=openai_api_key,
        temperature=0
    )
    system_template = """You are a virtual assistant designed to calculate the commission for an NFT. The NFT is '{nft}', the service is '{service}', the referral code is '{referral_code}', and the commission percentage is '{commission_percentage}'."""
    system_message_prompt = SystemMessagePromptTemplate.from_template(
        system_template)
    human_template = """Please calculate the commission for the NFT '{nft}' using the service '{service}', referral code '{referral_code}', and commission percentage of '{commission_percentage}'."""
    human_message_prompt = HumanMessagePromptTemplate.from_template(
        human_template)
    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )

    chain = LLMChain(llm=chat, prompt=chat_prompt)
    result = chain.run(nft=nft, service=service, referral_code=referral_code,
                       commission_percentage=commission_percentage)
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


st.sidebar.markdown("""'''
# How to use

1. Enter your [OpenAI API key](https://platform.openai.com/account/api-keys) above🔑
2. Input the NFT you have in the provided text box.
3. Enter the details of the service you are using in the next text box.
4. Provide your referral code in the designated text box.
5. Specify the commission percentage in the subsequent text box.
6. Once all the inputs are filled, the application will automatically calculate the commission for the NFT.
7. The calculated commission will be displayed to you.
'''""")


st.sidebar.markdown("# About")
st.sidebar.markdown("NFTs: Earning, Eh? is an innovative application that interacts with NFTs, using them as referral codes. For each service sold, the NFT used as a referral code earns a 10% commission. This app revolutionizes the way we perceive NFTs, turning them into a source of passive income.")

with st.form(key="form"):
    st.title('NFTs: Earning, Eh?')
    nft = st.text_input("Enter NFT")
    service = st.text_input("Enter service details")
    referral_code = st.text_input("Enter referral code")
    commission_percentage = st.number_input(
        "Enter the commission percentage", min_value=0.0, max_value=100.0)

    submit_button = st.form_submit_button(label='Submit')
    if not openai_api_key.startswith('sk-'):
        st.warning('Please enter your OpenAI API key!', icon='⚠')
    if submit_button:

        if not openai_api_key.startswith('sk-'):
            st.warning('Please enter your OpenAI API key!', icon='⚠')
            commission = ""
        elif (isinstance(nft, bool) or nft) and (isinstance(service, bool) or service) and (isinstance(referral_code, bool) or referral_code) and (isinstance(commission_percentage, bool) or commission_percentage):
            with st.spinner('DemoGPT is working on it. It takes less than 10 seconds...'):
                commission = nftCommissionCalculator(
                    nft, service, referral_code, commission_percentage)
        else:
            commission = ""

        st.markdown(commission)
