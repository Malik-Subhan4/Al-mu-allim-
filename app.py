import streamlit as st
# ... (keep your previous imports)

# Essential for Mobile: Set layout to "centered" for a narrow phone view
st.set_page_config(
    page_title="Al-Mu'allim VA", 
    page_icon="🕌", 
    layout="centered"
)

# Custom CSS to make text and buttons large enough for touch screens
st.markdown("""
    <style>
    /* Make chat text larger for mobile readability */
    .stMarkdown { font-size: 18px; }
    
    /* Ensure the input box doesn't get hidden by the keyboard */
    .stChatInput { margin-bottom: 70px; }
    
    /* Make buttons easy to tap with a thumb */
    .stButton>button {
        height: 3em;
        width: 100%;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
