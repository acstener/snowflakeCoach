import streamlit as st
from dotenv import load_dotenv
from snowflake.snowpark.session import Session
import os
from snowflake.core import Root
import pandas as pd
import json

# Load environment variables
load_dotenv()

# Constants
NUM_CHUNKS = 3
SLIDE_WINDOW = 7  # Number of previous conversations to remember

# Initialize session
connection_params = {
    "account": os.getenv("SNOWFLAKE_ACCOUNT"),
    "user": os.getenv("SNOWFLAKE_USER"),
    "password": os.getenv("SNOWFLAKE_USER_PASSWORD"),
    "role": os.getenv("SNOWFLAKE_ROLE"),
    "database": os.getenv("SNOWFLAKE_DATABASE"),
    "schema": os.getenv("SNOWFLAKE_SCHEMA"),
    "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE")
}

session = Session.builder.configs(connection_params).create()
root = Root(session)

# Get search service
svc = root.databases[os.getenv("SNOWFLAKE_DATABASE")]\
    .schemas[os.getenv("SNOWFLAKE_SCHEMA")]\
    .cortex_search_services["CC_SEARCH_SERVICE_CS"]

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

def get_similar_chunks_search_service(query):
    if st.session_state.category_value == "ALL":
        response = svc.search(query, ["chunk", "relative_path", "category"], limit=NUM_CHUNKS)
    else:
        filter_obj = {"@eq": {"category": st.session_state.category_value}}
        response = svc.search(query, ["chunk", "relative_path", "category"], 
                            filter=filter_obj, limit=NUM_CHUNKS)
    
    if st.session_state.debug:
        st.sidebar.json(response.json())
    return response.json()

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
        You are an expert chat assistant that extracts information from the CONTEXT provided
        between <context> and </context> tags.
        You offer a chat experience considering the information included in the CHAT HISTORY
        provided between <chat_history> and </chat_history> tags.
        When answering the question contained between <question> and </question> tags
        be concise and do not hallucinate. 
        If you don't have the information just say so.
        
        Do not mention the CONTEXT or CHAT HISTORY in your answer.
        Only answer the question if you can extract it from the CONTEXT provided.
        
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

def config_sidebar():
    st.sidebar.selectbox('Select your model:', (
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

    categories = session.sql("select category from docs_chunks_table group by category").collect()
    cat_list = ['ALL'] + [cat.CATEGORY for cat in categories]
    st.sidebar.selectbox('Select product category:', cat_list, key="category_value")

    st.sidebar.checkbox('Remember chat history?', key="use_chat_history", value=True)
    st.sidebar.checkbox('Debug mode', key="debug", value=False)
    if st.sidebar.button("Clear Chat"):
        st.session_state.messages = []

def main():
    st.title("💬 Document Chat Assistant")
    
    # Initialize
    init_messages()
    config_sidebar()
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if question := st.chat_input("Ask about your documents..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
            
        # Generate and display response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            with st.spinner(f"Thinking..."):
                prompt, relative_paths = create_prompt(question)
                cmd = "select snowflake.cortex.complete(?, ?) as response"
                df_response = session.sql(cmd, params=[st.session_state.model_name, prompt]).collect()
                response = df_response[0].RESPONSE
                message_placeholder.markdown(response)
                
                # Show related documents
                if relative_paths != "None":
                    with st.sidebar.expander("📄 Related Documents"):
                        for path in relative_paths:
                            url_query = f"""
                            select GET_PRESIGNED_URL(@docs, '{path}', 360) as URL_LINK 
                            from directory(@docs)
                            """
                            url = session.sql(url_query).to_pandas().iloc[0]['URL_LINK']
                            st.sidebar.markdown(f"[{path}]({url})")
        
        # Save assistant response
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()