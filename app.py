import os
from exa_py import Exa
import openai
from datetime import datetime, timedelta

class NewsResearchAssistant:
    def __init__(self, exa_api_key, openai_api_key):
        self.exa = Exa(exa_api_key)
        openai.api_key = openai_api_key
        
    def generate_search_query(self, user_question):
        """Convert user question into a search query using GPT."""
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Generate a concise search query based on the user's question. Return only the search query."},
                {"role": "user", "content": user_question}
            ]
        )
        return completion.choices[0].message.content
    
    def search_recent_articles(self, query, days_ago=7):
        """Search for recent articles using Exa."""
        date_cutoff = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        search_response = self.exa.search_and_contents(
            query,
            use_autoprompt=True,
            start_published_date=date_cutoff
        )
        return search_response.results
    
    def summarize_article(self, article_text):
        """Summarize article content using GPT."""
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Provide a brief, informative summary of the article in 2-3 sentences."},
                {"role": "user", "content": article_text}
            ]
        )
        return completion.choices[0].message.content
    
    def research(self, user_question, num_articles=3):
        """Main research function that combines search and summarization."""
        # Generate search query
        search_query = self.generate_search_query(user_question)
        print(f"🔍 Search query: {search_query}\n")
        
        # Get recent articles
        articles = self.search_recent_articles(search_query)
        
        # Process top articles
        summaries = []
        for i, article in enumerate(articles[:num_articles]):
            print(f"\n📰 Article {i+1}: {article.title}")
            print(f"🔗 URL: {article.url}")
            
            summary = self.summarize_article(article.text)
            print(f"📝 Summary: {summary}\n")
            summaries.append({
                "title": article.title,
                "url": article.url,
                "summary": summary
            })
            
        return summaries

# Example usage
def main():
    # Initialize with your API keys
    assistant = NewsResearchAssistant(
        exa_api_key="your_exa_api_key",
        openai_api_key="your_openai_api_key"
    )
    
    # Example research question
    question = "What are the latest developments in quantum computing?"
    results = assistant.research(question)

if __name__ == "__main__":
    main()
