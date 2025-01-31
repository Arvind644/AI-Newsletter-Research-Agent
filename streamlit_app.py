import streamlit as st
from app import NewsResearchAssistant
import os

# Page configuration
st.set_page_config(
    page_title="AI News Research Assistant",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .article-box {
        padding: 20px;
        border-radius: 5px;
        border: 1px solid #ddd;
        margin: 10px 0;
    }
    .url-link {
        color: #4287f5;
        text-decoration: none;
    }
    </style>
""", unsafe_allow_html=True)

def initialize_assistant():
    """Initialize the NewsResearchAssistant with API keys."""
    # Get API keys from environment variables or Streamlit secrets
    exa_api_key = os.getenv("EXA_API_KEY") or st.secrets["EXA_API_KEY"]
    openai_api_key = os.getenv("OPENAI_API_KEY") or st.secrets["OPENAI_API_KEY"]
    
    return NewsResearchAssistant(exa_api_key, openai_api_key)

def main():
    # Header
    st.title("🔍 AI News Research Assistant")
    st.markdown("Get instant summaries of the latest news on any topic.")
    
    # Sidebar controls
    with st.sidebar:
        st.header("Search Settings")
        num_articles = st.slider("Number of articles to analyze", 1, 10, 3)
        days_ago = st.slider("Search articles from last N days", 1, 30, 7)
    
    # Main search interface
    question = st.text_input("Enter your research question:", 
                           placeholder="e.g., What are the latest developments in quantum computing?")
    
    if st.button("Research", type="primary"):
        if question:
            try:
                # Initialize assistant
                assistant = initialize_assistant()
                
                # Show progress
                with st.spinner("🔍 Searching for relevant articles..."):
                    # Modify the research method to include days_ago parameter
                    results = assistant.research(question, num_articles=num_articles)
                
                # Display results
                st.success(f"Found {len(results)} relevant articles!")
                
                for i, article in enumerate(results, 1):
                    with st.container():
                        st.markdown(f"""
                        <div class="article-box">
                            <h3>📰 Article {i}: {article['title']}</h3>
                            <p><a href="{article['url']}" target="_blank" class="url-link">🔗 Read full article</a></p>
                            <p><strong>Summary:</strong> {article['summary']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                # Add option to download results
                if results:
                    st.download_button(
                        label="Download Results",
                        data=str(results),
                        file_name="research_results.txt",
                        mime="text/plain"
                    )
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please enter a research question.")
    
    # Footer
    st.markdown("---")
    st.markdown("Powered by Exa AI and OpenAI")

if __name__ == "__main__":
    main() 