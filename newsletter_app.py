import streamlit as st
from newsletter_agent import NewsletterAgent
import os
import json
from datetime import datetime
import base64
from pathlib import Path

# Function to load and encode the image
def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Load the logo
try:
    logo_path = "public/buildclub-long.png"
    encoded_logo = get_base64_encoded_image(logo_path)
    logo_html = f'<img src="data:image/png;base64,{encoded_logo}" style="height: 80px; width: auto;">'
except Exception as e:
    st.warning(f"Error loading logo: {str(e)}")
    logo_html = ""

# Configure page settings
st.set_page_config(
    page_title="AI Newsletter Research Agent",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for header and footer
st.markdown("""
    <style>
    /* Main styles */
    .main {
        background-color: white !important;
    }
    
    /* Header styles */
    .header {
        padding: 1.5rem 1rem;
        background-color: white;
        border-bottom: 1px solid #f0f0f0;
        margin: -6rem -4rem 2rem -4rem;
    }
    
    .header-content {
        max-width: 1200px;
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
    }
    
    .header-left {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .header-text {
        margin-left: 1rem;
    }
    
    .app-title {
        color: #262730;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 0;
    }
    
    .app-subtitle {
        color: #666;
        font-size: 1rem;
        margin: 0;
    }
    
    /* Footer styles */
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: white;
        padding: 1rem;
        text-align: center;
        border-top: 1px solid #f0f0f0;
    }
    
    .footer-content {
        color: #666;
        font-size: 0.8rem;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Header with logo
st.markdown(f"""
    <div class="header">
        <div class="header-content">
            <div class="header-left">
                {logo_html}
                <div class="header-text">
                    <h1 class="app-title">AI Newsletter Research Agent</h1>
                    <p class="app-subtitle">Create comprehensive research newsletters automatically</p>
                </div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

def load_topics():
    """Load saved topic configurations."""
    try:
        with open("topics.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Topics configuration file not found!")
        return {}

def initialize_agent():
    """Initialize the NewsletterAgent with API keys."""
    exa_api_key = os.getenv("EXA_API_KEY") or st.secrets["EXA_API_KEY"]
    openai_api_key = os.getenv("OPENAI_API_KEY") or st.secrets["OPENAI_API_KEY"]
    
    return NewsletterAgent(exa_api_key, openai_api_key)

def main():
    # Load topics configuration
    topics_config = load_topics()
    
    # Remove the duplicate title since it's already in the header
    st.markdown("Generate comprehensive AI research newsletters automatically.")
    
    # Sidebar settings
    with st.sidebar:
        st.markdown("### Newsletter Settings")
        
        # Custom Search Input
        st.markdown("#### Custom Search")
        custom_search = st.text_input(
            "Enter custom search terms",
            placeholder="e.g., Large Language Models, Computer Vision",
            help="Enter specific topics or keywords you want to research"
        )
        
        # Add a divider
        st.markdown("---")
        
        # Topic Categories from topics.json
        st.markdown("#### Topic Categories")
        st.markdown("Select categories and subtopics:")
        
        selected_topics = []
        
        # Add custom search terms if provided
        if custom_search:
            custom_topics = [topic.strip() for topic in custom_search.split(",")]
            selected_topics.extend(custom_topics)
        
        # Create expandable sections for each main category
        for category, subtopics in topics_config.items():
            with st.expander(category):
                if st.checkbox(f"Select all {category}", key=f"all_{category}"):
                    selected_topics.extend(subtopics)
                else:
                    for subtopic in subtopics:
                        if st.checkbox(subtopic, key=subtopic):
                            selected_topics.append(subtopic)
        
        # Email Settings
        st.markdown("#### Email Settings")
        enable_email = st.checkbox("Enable email delivery")
    
    # Main content area
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
                    
                    # Display success message
                    st.success(f"Newsletter generated successfully! Saved as {filename}")
                    
                    # Show selected topics
                    st.markdown("### Selected Topics for Research")
                    for topic in selected_topics:
                        st.markdown(f"- {topic}")
                    
                    # Show preview
                    st.markdown("### Newsletter Preview")
                    st.markdown(newsletter_content)
                    
                    # Download buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            "📥 Download as PDF",
                            data=newsletter_content,
                            file_name=filename.replace('.md', '.pdf'),
                            mime="application/pdf",
                            help="Download the newsletter in PDF format"
                        )
                    with col2:
                        st.download_button(
                            "📝 Download as Markdown",
                            data=newsletter_content,
                            file_name=filename,
                            mime="text/markdown",
                            help="Download the newsletter in Markdown format"
                        )
                    
                    # Send email if enabled
                    if enable_email:
                        with st.spinner("📧 Sending newsletter via email..."):
                            # You'll need to configure email settings
                            email_config = {
                                'smtp_server': 'smtp.example.com',
                                'smtp_port': 465,
                                'username': 'your_email@example.com',
                                'password': 'your_password',
                                'from_email': 'your_email@example.com',
                                'to_email': 'recipient@example.com'
                            }
                            agent.send_newsletter(newsletter_content, email_config)
                            st.success("Newsletter sent successfully via email!")
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please enter custom search terms or select topics from the categories.")
    
    # Footer
    st.markdown("---")
    st.markdown("Powered by Exa AI and OpenAI")

# Footer
st.markdown("""
    <div class="footer">
        <div class="footer-content">
            © 2024 <a href="https://buildclub.ai"> Build Club </a> | AI Newsletter Research Agent
        </div>
    </div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()