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
        
        /* Custom styling for the Generate Protocol button */
        .stButton button[kind="primary"] {
            background-color: #1E293B !important;
            border: none !important;
            color: white !important;
            transition: background-color 0.3s ease !important;
        }
        
        .stButton button[kind="primary"]:hover {
            background-color: #334155 !important;
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
    if "use_chat_history" not in st.session_state:
        st.session_state.use_chat_history = True
    if "category_value" not in st.session_state:
        st.session_state.category_value = "ALL"
    if "model_name" not in st.session_state:
        st.session_state.model_name = "mixtral-8x7b"

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

def generate_protocol():
    if len(st.session_state.messages) < 2:
        st.warning("Have a conversation with Huberman AI first to generate a protocol!")
        return None
        
    # Get the last few exchanges
    recent_messages = st.session_state.messages[-6:]  # Last 3 Q&A pairs
    conversation = "\n".join([f"{'Q' if msg['role'] == 'user' else 'A'}: {msg['content']}" for msg in recent_messages])
    
    # Extract main topics from conversation for RAG search
    topic_extraction_prompt = f"""
    Extract the main health/wellness topics from this conversation as a comma-separated list:
    {conversation}
    Answer with only the topics, no explanation.
    """
    cmd = "select snowflake.cortex.complete(?, ?) as response"
    topics_response = session.sql(cmd, params=[st.session_state.model_name, topic_extraction_prompt]).collect()
    topics = topics_response[0].RESPONSE
    
    # Get relevant research for each topic
    all_research = []
    for topic in topics.split(','):
        research = get_similar_chunks_search_service(topic.strip())
        research_json = json.loads(research)
        if 'results' in research_json:
            all_research.extend([r['chunk'] for r in research_json['results']])
    
    # Combine research findings
    research_context = "\n\n".join(all_research) if all_research else "No specific research found."
    
    protocol_prompt = f"""
    You are Dr. Andrew Huberman. Based on this conversation and scientific literature, create an actionable protocol.
    
    Conversation:
    {conversation}
    
    Scientific Literature:
    {research_context}
    
    Create a detailed protocol with the following sections (use emojis for headers):
    
    🎯 OBJECTIVE
    - Clear statement of the goal based on the conversation
    
    ⚡ MECHANISM
    - Brief explanation of the key biological/neurological mechanisms
    - Reference specific research findings where possible
    
    📋 PROTOCOL STEPS
    - Detailed day-by-day or step-by-step instructions
    - Include specific timings and durations
    - Base recommendations on the scientific literature provided
    
    ⚠️ IMPORTANT CONSIDERATIONS
    - Key things to watch out for
    - Common mistakes to avoid
    - Contraindications from the research
    
    📊 MEASURING PROGRESS
    - How to track success
    - What markers to monitor
    - Evidence-based metrics from the literature
    
    Format in clean markdown with clear sections and bullet points.
    Be specific with numbers, timings, and measurements where possible.
    Ground all recommendations in the scientific literature provided.
    """
    
    try:
        cmd = "select snowflake.cortex.complete(?, ?) as response"
        df_response = session.sql(cmd, params=[st.session_state.model_name, protocol_prompt]).collect()
        return df_response[0].RESPONSE
    except Exception as e:
        st.error(f"Error generating protocol: {str(e)}")
        return None

def main():
    # Initialize
    init_messages()
    
    # Title and subtitle
    st.title("Chat with Huberman AI")
    st.markdown("Powered by Snowflake Cortex and Streamlit 🚀")
    
    # Model selector and Generate Protocol on same line
    st.markdown("Select model:")
    col1, col2 = st.columns([3, 1])
    with col1:
        st.selectbox('', (  # Empty label since we have the text above
            'mixtral-8x7b',
            'snowflake-arctic',
            'mistral-large',
            'llama3-8b',
            'llama3-70b',
            'reka-flash',
            'mistral-7b',
            'llama2-70b-chat',
            'gemma-7b'
        ), key="model_name", label_visibility="collapsed")
    
    with col2:
        if st.button("🎯 Generate Protocol", use_container_width=True, type="primary"):
            with st.spinner("Creating your personalized protocol..."):
                protocol = generate_protocol()
                if protocol:
                    st.session_state.show_protocol = protocol
                    st.rerun()
    
    st.markdown("---")  # Add a separator
    
    # Show protocol in modal-like container if generated
    if 'show_protocol' in st.session_state and st.session_state.show_protocol:
        with st.expander("📋 Your Personalized Protocol", expanded=True):
            st.markdown(st.session_state.show_protocol)
            if st.button("Close"):
                del st.session_state.show_protocol
                st.rerun()
    
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
            
            # Generate everything at once under one spinner
            with st.spinner("Scanning the literature..."):
                # Get response and references
                prompt, relative_paths = create_prompt(question)
                cmd = "select snowflake.cortex.complete(?, ?) as response"
                df_response = session.sql(cmd, params=[st.session_state.model_name, prompt]).collect()
                response = df_response[0].RESPONSE
                
                # Get URLs for references if any
                urls = {}
                if relative_paths != "None":
                    for path in relative_paths:
                        url_query = f"""
                        select GET_PRESIGNED_URL(@docs, '{path}', 360) as URL_LINK 
                        from directory(@docs)
                        """
                        urls[path] = session.sql(url_query).to_pandas().iloc[0]['URL_LINK']
            
            # Display everything without spinners
            message_placeholder.markdown(response)
            if urls:
                with st.expander("Further reading:"):
                    for path, url in urls.items():
                        st.markdown(f"[{path}]({url})")
        
        # Save assistant response
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main() 