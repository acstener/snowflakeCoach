import streamlit as st
from dotenv import load_dotenv
from snowflake.snowpark.session import Session
import os
from snowflake.core import Root
import json
import pandas as pd

# Load environment variables
load_dotenv()

# Constants
NUM_CHUNKS = 3
COLUMNS = ["chunk", "relative_path", "category"]

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

def config_options():
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

    # Get categories from database
    categories = session.sql("select category from docs_chunks_table group by category").collect()
    cat_list = ['ALL']
    for cat in categories:
        cat_list.append(cat.CATEGORY)
    
    st.sidebar.selectbox('Select what products you are looking for', cat_list, key="category_value")

def get_similar_chunks_search_service(query):
    if st.session_state.category_value == "ALL":
        response = svc.search(query, COLUMNS, limit=NUM_CHUNKS)
    else:
        filter_obj = {"@eq": {"category": st.session_state.category_value}}
        response = svc.search(query, COLUMNS, filter=filter_obj, limit=NUM_CHUNKS)
    
    return response.json()

def create_prompt(question):
    if st.session_state.rag:
        prompt_context = get_similar_chunks_search_service(question)
        
        prompt = f"""
           You are an expert chat assistance that extracts information from the CONTEXT provided
           between <context> and </context> tags.
           When answering the question contained between <question> and </question> tags
           be concise and do not hallucinate. 
           If you don't have the information just say so.
           Only answer the question if you can extract it from the CONTEXT provided.
           
           Do not mention the CONTEXT used in your answer.
    
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
    else:
        prompt = f"Question: {question}\nAnswer:"
        relative_paths = "None"
    
    return prompt, relative_paths

def complete(question):
    prompt, relative_paths = create_prompt(question)
    cmd = "select snowflake.cortex.complete(?, ?) as response"
    df_response = session.sql(cmd, params=[st.session_state.model_name, prompt]).collect()
    return df_response, relative_paths

def main():
    st.title("📝 Chat Document Assistant with Snowflake Cortex")
    
    # Show available documents
    st.write("Available documents:")
    docs_available = session.sql("ls @docs").collect()
    list_docs = []
    for doc in docs_available:
        list_docs.append(doc["name"])
    st.dataframe(list_docs)

    # Configure sidebar options
    config_options()
    st.session_state.rag = st.sidebar.checkbox('Use your own documents as context?')

    # Search input
    question = st.text_input(
        "Enter your question:",
        placeholder="Is there any special lubricant to be used with the premium bike?",
        label_visibility="collapsed"
    )

    if question:
        response, relative_paths = complete(question)
        res_text = response[0].RESPONSE
        st.markdown(res_text)

        # Show related documents
        if relative_paths != "None":
            with st.sidebar.expander("Related Documents"):
                for path in relative_paths:
                    cmd2 = f"select GET_PRESIGNED_URL(@docs, '{path}', 360) as URL_LINK from directory(@docs)"
                    df_url_link = session.sql(cmd2).to_pandas()
                    url_link = df_url_link._get_value(0, 'URL_LINK')
                    display_url = f"Doc: [{path}]({url_link})"
                    st.sidebar.markdown(display_url)

if __name__ == "__main__":
    main()