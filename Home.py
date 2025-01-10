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
            padding: 2.5rem 2rem !important;
            border-radius: 16px !important;
            text-align: center !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
            transition: transform 0.2s ease-in-out !important;
        }
        
        .expert-card:hover {
            transform: translateY(-4px) !important;
            border-color: rgba(255, 255, 255, 0.2) !important;
        }
        
        .expert-image {
            width: 100px !important;
            height: 100px !important;
            border-radius: 50px !important;
            margin-bottom: 1.5rem !important;
            border: 2px solid rgba(255, 255, 255, 0.1) !important;
        }
        
        /* Expert info */
        .expert-role {
            color: #64748B !important;
            text-transform: uppercase !important;
            font-size: 0.75rem !important;
            letter-spacing: 0.1em !important;
            margin-bottom: 0.75rem !important;
            font-weight: 500 !important;
        }
        
        .expert-name {
            color: white !important;
            font-size: 1.5rem !important;
            font-weight: 600 !important;
            margin: 0.75rem 0 !important;
        }
        
        .expert-bio {
            color: #94A3B8 !important;
            font-size: 0.875rem !important;
            line-height: 1.6 !important;
            margin-bottom: 1.5rem !important;
            opacity: 0.8 !important;
        }
        
        /* Buttons */
        .stButton button {
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: white !important;
            padding: 0.75rem 1.5rem !important;
            border-radius: 8px !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 500 !important;
            font-size: 0.875rem !important;
            transition: all 0.2s ease-in-out !important;
            width: auto !important;
            min-width: 200px !important;
        }
        
        .stButton button:hover {
            background: rgba(255, 255, 255, 0.1) !important;
            border-color: rgba(255, 255, 255, 0.2) !important;
            transform: translateY(-2px) !important;
        }
        
        /* Container spacing */
        .expert-grid {
            display: grid !important;
            grid-template-columns: repeat(3, 1fr) !important;
            gap: 2rem !important;
            margin-top: 2rem !important;
            padding: 0 1rem !important;
        }
        
        /* Center buttons */
        .stButton {
            display: flex !important;
            justify-content: center !important;
            margin-top: 1rem !important;
        }
        
        /* Primary button */
        .primary-button {
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            background: linear-gradient(135deg, #4F46E5 0%, #3730A3 100%) !important;
            color: white !important;
            padding: 0.875rem 2rem !important;
            border-radius: 8px !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 1rem !important;
            font-weight: 500 !important;
            text-decoration: none !important;
            transition: all 0.2s ease-in-out !important;
            border: none !important;
            margin: 1rem 0 3rem 0 !important;
            box-shadow: 0 4px 20px rgba(79, 70, 229, 0.15) !important;
            backdrop-filter: blur(8px) !important;
            -webkit-backdrop-filter: blur(8px) !important;
        }
        
        .primary-button:hover {
            background: linear-gradient(135deg, #4338CA 0%, #312E81 100%) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(79, 70, 229, 0.25) !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

def main():
    # Hero Section
    st.markdown(
        """
        <div style="text-align: center; max-width: 1000px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; justify-content: center;">
            <h1>Expert guidance on<br>health & wellness</h1>
            <p style="font-size: 1.2rem; margin-bottom: 2rem; max-width: 800px;">
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
    st.markdown('<div class="expert-grid">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            """
            <div class="expert-card">
                <img src="https://yt3.googleusercontent.com/5ONImZvpa9_hYK12Xek2E2JLzRc732DWsZMX2F-AZ1cTutTQLBuAmcEtFwrCgypqJncl5HrV2w=s160-c-k-c0x00ffffff-no-rj" 
                    class="expert-image">
                <div class="expert-role">Stanford neuroscientist</div>
                <div class="expert-name">Andrew Huberman</div>
                <div class="expert-bio">Host of the Huberman Lab podcast. Expert in neuroscience and performance.</div>
                <div style="margin-top: auto;">
                    <a href="1_chat" style="
                        display: inline-block;
                        background: rgba(255, 255, 255, 0.05);
                        border: 1px solid rgba(255, 255, 255, 0.1);
                        color: white;
                        padding: 0.75rem 1.5rem;
                        border-radius: 8px;
                        font-family: 'Inter', sans-serif;
                        font-weight: 500;
                        font-size: 0.875rem;
                        text-decoration: none;
                        transition: all 0.2s ease-in-out;
                        min-width: 160px;
                    ">Chat with Andrew</a>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            """
            <div class="expert-card">
                <img src="https://media.gq-magazine.co.uk/photos/63e3cd12cc78ab15a94a2458/1:1/w_1080,h_1080,c_limit/_Bryan-Johnson-2.jpg" 
                    class="expert-image">
                <div class="expert-role">Tech entrepreneur turned biohacker</div>
                <div class="expert-name">Bryan Johnson</div>
                <div class="expert-bio">Known for Blueprint protocol and anti-aging techniques.</div>
                <div style="margin-top: auto;">
                    <a href="1_chat" style="
                        display: inline-block;
                        background: rgba(255, 255, 255, 0.05);
                        border: 1px solid rgba(255, 255, 255, 0.1);
                        color: white;
                        padding: 0.75rem 1.5rem;
                        border-radius: 8px;
                        font-family: 'Inter', sans-serif;
                        font-weight: 500;
                        font-size: 0.875rem;
                        text-decoration: none;
                        transition: all 0.2s ease-in-out;
                        min-width: 160px;
                    ">Chat with Bryan</a>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col3:
        st.markdown(
            """
            <div class="expert-card">
                <img src="https://www.buckinstitute.org/wp-content/uploads/2022/12/rhonda-patrick-1.png" 
                    class="expert-image">
                <div class="expert-role">Biochemist and expert</div>
                <div class="expert-name">Dr. Rhonda Patrick</div>
                <div class="expert-bio">Specializes in aging, cancer, and nutrition research.</div>
                <div style="margin-top: auto;">
                    <a href="1_chat" style="
                        display: inline-block;
                        background: rgba(255, 255, 255, 0.05);
                        border: 1px solid rgba(255, 255, 255, 0.1);
                        color: white;
                        padding: 0.75rem 1.5rem;
                        border-radius: 8px;
                        font-family: 'Inter', sans-serif;
                        font-weight: 500;
                        font-size: 0.875rem;
                        text-decoration: none;
                        transition: all 0.2s ease-in-out;
                        min-width: 160px;
                    ">Chat with Dr. Rhonda</a>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main() 