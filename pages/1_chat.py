# Moving our existing chat code here
import streamlit as st
from snowflake.snowpark.session import Session
import os
from snowflake.core import Root
import pandas as pd
import json

# Set page config
st.set_page_config(
    page_title="Chat with Expert",
    layout="wide",
    menu_items={} # This removes the menu with navigation
)

# Custom CSS for modern look
st.markdown(
    """
    <style>
        /* Import Inter font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap');
        
        /* Hide ALL navigation elements */
        .stApp > header {
            display: none !important;
        }
        
        /* Hide sidebar completely */
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        
        /* Hide navigation links */
        .css-1d391kg, .css-1lsmgbg {
            display: none !important;
        }
        
        /* Model selector styling */
        .model-selector {
            max-width: 300px !important;
            margin: 1rem auto !important;
        }
        
        /* Apply Inter font to all elements */
        .stApp, .stMarkdown, p, h1, h2, h3, .stButton button, 
        .stTextInput input, .stSelectbox select, .stCheckbox label {
            font-family: 'Inter', sans-serif !important;
        }
        
        /* Chat message styling */
        .stChatMessage {
            font-family: 'Inter', sans-serif !important;
        }
        
        .stChatMessage p {
            font-family: 'Inter', sans-serif !important;
            font-size: 1.1rem !important;
            line-height: 1.6 !important;
        }
        
        /* Title styling */
        h1 {
            font-family: 'Inter', sans-serif !important;
            font-weight: 700 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Constants
NUM_CHUNKS = 3
SLIDE_WINDOW = 7  # Number of previous conversations to remember

# Validate Snowflake credentials
required_snowflake_params = ["account", "user", "password", "role", "database", "schema", "warehouse"]
missing_params = []

for param in required_snowflake_params:
    if not st.secrets.snowflake.get(param):
        missing_params.append(param)

if missing_params:
    st.error(f"Missing required Snowflake credentials: {', '.join(missing_params)}")
    st.info("Please add these credentials to your .streamlit/secrets.toml file or Streamlit Cloud secrets.")
    st.stop()

# Initialize session
connection_params = {
    "account": st.secrets.snowflake["account"],
    "user": st.secrets.snowflake["user"],
    "password": st.secrets.snowflake["password"],
    "role": st.secrets.snowflake["role"],
    "database": st.secrets.snowflake["database"],
    "schema": st.secrets.snowflake["schema"],
    "warehouse": st.secrets.snowflake["warehouse"]
}

try:
    session = Session.builder.configs(connection_params).create()
    root = Root(session)

    # Get search service
    svc = root.databases[st.secrets.snowflake["database"]]\
        .schemas[st.secrets.snowflake["schema"]]\
        .cortex_search_services["CC_SEARCH_SERVICE_CS"]
except Exception as e:
    st.error(f"Failed to connect to Snowflake: {str(e)}")
    st.info("Please check your Snowflake credentials in .streamlit/secrets.toml")
    st.stop()

def get_similar_chunks_search_service(query):
    if st.session_state.category_value == "ALL":
        response = svc.search(query, ["chunk", "relative_path", "category"], limit=NUM_CHUNKS)
    else:
        filter_obj = {"@eq": {"category": st.session_state.category_value}}
        response = svc.search(query, ["chunk", "relative_path", "category"], 
                            filter=filter_obj, limit=NUM_CHUNKS)
    return response.json()

def init_messages():
    if "messages" not in st.session_state:
        st.session_state.messages = []

def get_chat_history():
    chat_history = []
    start_index = max(0, len(st.session_state.messages) - SLIDE_WINDOW)
    for i in range(start_index, len(st.session_state.messages) - 1):
        chat_history.append(st.session_state.messages[i])
    return chat_history

def summarize_conversation(chat_history, question):
    prompt = f"""
        Based on the chat history below and the question, generate a query that extends the question
        with the chat history provided. The query should be in natural language.
        Answer with only the query. Do not add any explanation.
        
        <chat_history>
        {chat_history}
        </chat_history>
        <question>
        {question}
        </question>
        """
    
    cmd = "select snowflake.cortex.complete(?, ?) as response"
    df_response = session.sql(cmd, params=[st.session_state.model_name, prompt]).collect()
    return df_response[0].RESPONSE.replace("'", "")

def create_prompt(question):
    if st.session_state.use_chat_history:
        chat_history = get_chat_history()
        if chat_history:
            summary = summarize_conversation(chat_history, question)
            prompt_context = get_similar_chunks_search_service(summary)
        else:
            prompt_context = get_similar_chunks_search_service(question)
    else:
        prompt_context = get_similar_chunks_search_service(question)
        chat_history = ""

    prompt = f"""
        You are Dr. Andrew Huberman, a neuroscientist and professor at Stanford who extracts information from the scientific literature provided
        between <context> and </context> tags.
        You offer science-based protocols and mechanistic insights considering the information included in the CHAT HISTORY
        provided between <chat_history> and </chat_history> tags.
        When answering the question contained between <question> and </question> tags
        be direct about the peer-reviewed evidence and cite specific mechanisms. 
        If you don't have peer-reviewed research to support an answer, just say so.
        
        Do not mention the CONTEXT or CHAT HISTORY in your answer.
        Only provide protocols and insights if they are supported by the research CONTEXT provided.
        
        <chat_history>
        {chat_history}
        </chat_history>
        <context>          
        {prompt_context}
        </context>
        <question>  
        {question}
        </question>
        Answer: 
        """
    
    json_data = json.loads(prompt_context)
    relative_paths = set(item['relative_path'] for item in json_data['results'])
    return prompt, relative_paths

def config_model_selector():
    # Create three columns for centering
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.selectbox('Select your model:', (
            'mixtral-8x7b',
            'snowflake-arctic',
            'mistral-large',
            'llama3-8b',
            'llama3-70b',
            'reka-flash',
            'mistral-7b',
            'llama2-70b-chat',
            'gemma-7b'
        ), key="model_name")

    # Setting default values
    if "use_chat_history" not in st.session_state:
        st.session_state.use_chat_history = True
    if "category_value" not in st.session_state:
        st.session_state.category_value = "ALL"

def main():
    # Initialize
    init_messages()
    
    # Add model selector above title
    config_model_selector()
    
    st.title("Chat with Huberman AI")
    st.text("Powered by Snowflake Cortex and Streamlit 🚀")

    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if question := st.chat_input("Ask about health, nutrition or exercise..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
            
        # Generate and display response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            with st.spinner(f"Scanning the literature..."):
                prompt, relative_paths = create_prompt(question)
                cmd = "select snowflake.cortex.complete(?, ?) as response"
                df_response = session.sql(cmd, params=[st.session_state.model_name, prompt]).collect()
                response = df_response[0].RESPONSE
                message_placeholder.markdown(response)
                
                # Show related documents in a container below the message
                if relative_paths != "None":
                    with st.expander("Further reading:"):
                        for path in relative_paths:
                            url_query = f"""
                            select GET_PRESIGNED_URL(@docs, '{path}', 360) as URL_LINK 
                            from directory(@docs)
                            """
                            url = session.sql(url_query).to_pandas().iloc[0]['URL_LINK']
                            st.markdown(f"[{path}]({url})")
        
        # Save assistant response
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main() 