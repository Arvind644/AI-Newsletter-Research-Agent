import streamlit as st
from newsletter_agent import NewsletterAgent
import os
import json
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="AI Newsletter Generator",
    page_icon="📰",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .newsletter-section {
        padding: 20px;
        border-radius: 5px;
        border: 1px solid #ddd;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

def initialize_agent():
    """Initialize the NewsletterAgent with API keys."""
    exa_api_key = os.getenv("EXA_API_KEY") or st.secrets["EXA_API_KEY"]
    openai_api_key = os.getenv("OPENAI_API_KEY") or st.secrets["OPENAI_API_KEY"]
    
    return NewsletterAgent(exa_api_key, openai_api_key)

def load_topics():
    """Load saved topic configurations."""
    try:
        with open("topics.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "AI & Machine Learning": ["Latest AI developments", "Machine learning breakthroughs"],
            "Technology": ["Quantum computing news", "Blockchain developments"],
            "Science": ["Space exploration updates", "Climate tech innovations"]
        }

def main():
    st.title("📰 AI Newsletter Generator")
    st.markdown("Generate comprehensive AI research newsletters automatically.")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Newsletter Settings")
        
        # Topic Management
        st.subheader("Topic Categories")
        topics = load_topics()
        
        selected_categories = st.multiselect(
            "Select categories to include:",
            options=list(topics.keys()),
            default=list(topics.keys())[:2]
        )
        
        # Collect all selected topics
        selected_topics = []
        for category in selected_categories:
            selected_topics.extend(topics[category])
        
        # Email Settings
        st.subheader("Email Settings")
        enable_email = st.checkbox("Enable email delivery")
        
        if enable_email:
            email_config = {
                "smtp_server": st.text_input("SMTP Server", "smtp.gmail.com"),
                "smtp_port": st.number_input("SMTP Port", value=465),
                "username": st.text_input("Email Username"),
                "password": st.text_input("Email Password", type="password"),
                "from_email": st.text_input("From Email"),
                "to_email": st.text_input("To Email")
            }
    
    # Main interface
    if st.button("Generate Newsletter", type="primary"):
        if selected_topics:
            try:
                agent = initialize_agent()
                
                with st.spinner("🔍 Researching topics and generating newsletter..."):
                    # Generate newsletter content
                    sections = agent.generate_newsletter_sections(selected_topics)
                    newsletter_content = agent.format_newsletter(sections)
                    
                    # Save newsletter
                    filename = agent.save_newsletter(newsletter_content)
                    
                    # Display preview
                    st.success(f"Newsletter generated successfully! Saved as {filename}")
                    
                    # Show preview
                    st.markdown("### Newsletter Preview")
                    st.markdown(newsletter_content)
                    
                    # Download option
                    st.download_button(
                        label="Download Newsletter",
                        data=newsletter_content,
                        file_name=filename,
                        mime="text/markdown"
                    )
                    
                    # Send email if enabled
                    if enable_email:
                        with st.spinner("📧 Sending newsletter via email..."):
                            agent.send_newsletter(newsletter_content, email_config)
                            st.success("Newsletter sent successfully via email!")
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please select at least one topic category.")
    
    # Footer
    st.markdown("---")
    st.markdown("Powered by Exa AI and OpenAI")

if __name__ == "__main__":
    main() 