import streamlit as st

# Hide the sidebar navigation
st.set_page_config(
    page_title="Health & Wellness AI Coach",
    initial_sidebar_state="collapsed",
    layout="wide"
)

# Custom CSS for modern look
st.markdown(
    """
    <style>
        /* Import Inter font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap');
        
        /* Hide sidebar */
        [data-testid="collapsedControl"] {
            display: none !important;
        }
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        
        /* Dark gradient background with pattern */
        .stApp {
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%) !important;
            background-attachment: fixed !important;
            background-image: radial-gradient(circle at 1px 1px, rgba(255, 255, 255, 0.05) 1px, transparent 0) !important;
            background-size: 40px 40px !important;
        }
        
        /* Basic styles */
        .stApp > header {
            background-color: transparent !important;
        }
        
        .block-container {
            padding: 5rem 2rem !important;
            max-width: 1140px !important;
            margin-left: auto !important;
            margin-right: auto !important;
        }
        
        /* Typography */
        h1 {
            font-family: 'Inter', sans-serif !important;
            font-size: 4rem !important;
            font-weight: 700 !important;
            color: white !important;
            line-height: 1.2 !important;
            margin-bottom: 1.5rem !important;
        }
        
        p {
            font-family: 'Inter', sans-serif !important;
            color: #94A3B8 !important;
        }
        
        /* Expert cards */
        .expert-card {
            background: rgba(15, 23, 42, 0.6) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            padding: 2rem !important;
            border-radius: 12px !important;
            text-align: center !important;
        }
        
        .expert-image {
            width: 120px !important;
            height: 120px !important;
            border-radius: 60px !important;
            margin-bottom: 1rem !important;
        }
        
        /* Buttons */
        .stButton button {
            width: 100% !important;
            background: rgba(255, 255, 255, 0.1) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: white !important;
            padding: 0.75rem 1.5rem !important;
            border-radius: 8px !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 500 !important;
        }
        
        .primary-button {
            display: inline-block !important;
            background: #3B82F6 !important;
            color: white !important;
            padding: 0.75rem 1.5rem !important;
            border-radius: 8px !important;
            text-decoration: none !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 500 !important;
            margin: 2rem 0 4rem 0 !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

def main():
    # Hero Section
    st.markdown(
        """
        <div style="text-align: center; max-width: 800px; margin: 0 auto;">
            <h1>Get expert guidance<br>on health, nutrition<br>and exercise</h1>
            <p style="font-size: 1.2rem; margin-bottom: 2rem;">
                Our AI coaches are trained on hours of speech transcripts from the leading experts in all things health. 
                Kick off the new year with personalized guidance.
            </p>
            <a href="1_chat" class="primary-button">Start chat now</a>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Add some space
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Expert Profiles Section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            """
            <div class="expert-card">
                <img src="https://yt3.googleusercontent.com/5ONImZvpa9_hYK12Xek2E2JLzRc732DWsZMX2F-AZ1cTutTQLBuAmcEtFwrCgypqJncl5HrV2w=s160-c-k-c0x00ffffff-no-rj" 
                    class="expert-image">
                <p style="color: #64748B; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 0.1em;">Stanford neuroscientist</p>
                <h3 style="color: white; font-size: 1.5rem; margin: 0.5rem 0;">Andrew Huberman</h3>
                <p style="font-size: 0.9rem; margin-bottom: 1rem;">Host of the Huberman Lab podcast. Expert in neuroscience and performance.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Chat with Andrew", key="huberman"):
            st.switch_page("pages/1_chat.py")
    
    with col2:
        st.markdown(
            """
            <div class="expert-card">
                <img src="https://media.gq-magazine.co.uk/photos/63e3cd12cc78ab15a94a2458/1:1/w_1080,h_1080,c_limit/_Bryan-Johnson-2.jpg" 
                    class="expert-image">
                <p style="color: #64748B; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 0.1em;">Tech entrepreneur turned biohacker</p>
                <h3 style="color: white; font-size: 1.5rem; margin: 0.5rem 0;">Bryan Johnson</h3>
                <p style="font-size: 0.9rem; margin-bottom: 1rem;">Known for Blueprint protocol and anti-aging techniques.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Chat with Bryan", key="bryan"):
            st.switch_page("pages/1_chat.py")
    
    with col3:
        st.markdown(
            """
            <div class="expert-card">
                <img src="https://www.buckinstitute.org/wp-content/uploads/2022/12/rhonda-patrick-1.png" 
                    class="expert-image">
                <p style="color: #64748B; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 0.1em;">Biochemist and expert</p>
                <h3 style="color: white; font-size: 1.5rem; margin: 0.5rem 0;">Dr. Rhonda Patrick</h3>
                <p style="font-size: 0.9rem; margin-bottom: 1rem;">Specializes in aging, cancer, and nutrition research.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Chat with Dr. Rhonda", key="rhonda"):
            st.switch_page("pages/1_chat.py")

if __name__ == "__main__":
    main() 