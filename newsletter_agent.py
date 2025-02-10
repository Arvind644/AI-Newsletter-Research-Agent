from app import NewsResearchAssistant
import openai
from datetime import datetime
import json
import markdown
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List

class NewsletterAgent:
    def __init__(self, exa_api_key, openai_api_key):
        self.research_assistant = NewsResearchAssistant(exa_api_key, openai_api_key)
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key
        
    def _chunk_text(self, text, max_tokens=3000):
        """Split text into chunks that won't exceed token limit."""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            # Approximate token count (words / 0.75)
            word_tokens = len(word) / 3
            if current_length + word_tokens > max_tokens:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = word_tokens
            else:
                current_chunk.append(word)
                current_length += word_tokens
                
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        return chunks

    def _generate_topic_analysis(self, topic, article_texts):
        """Generate an analytical overview of the topic using GPT."""
        # Combine articles but limit the content
        summaries = []
        for article in article_texts[:5]:  # Limit to 5 articles
            # Get a shorter version of each article
            summary = self._get_brief_summary(article)
            summaries.append(summary)
            
        combined_text = "\n\n".join(summaries)
        
        prompt = f"""Analyze these articles about {topic} and provide:
        1. Key trends (2-3 sentences)
        2. Important developments (2-3 points)
        3. Brief implications (1-2 sentences)
        Be concise and focused.
        
        Articles:
        {combined_text}
        """
        
        try:
            completion = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a concise newsletter writer and analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500  # Limit response length
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Analysis unavailable: {str(e)}"

    def _get_brief_summary(self, article_text):
        """Get a very brief summary of an article."""
        try:
            completion = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Summarize this article in 2-3 sentences."},
                    {"role": "user", "content": article_text[:1000]}  # Only use first 1000 chars
                ],
                max_tokens=150
            )
            return completion.choices[0].message.content
        except Exception as e:
            return "Summary unavailable"

    def generate_newsletter_sections(self, topics):
        """Generate newsletter content for multiple topics."""
        newsletter_sections = []
        
        for topic in topics:
            try:
                # Limit articles per topic
                articles = self.research_assistant.research(topic, num_articles=3)
                
                # Generate section analysis using GPT
                article_texts = [f"Title: {a['title']}\nSummary: {a['summary']}" 
                               for a in articles]
                
                analysis = self._generate_topic_analysis(topic, article_texts)
                
                newsletter_sections.append({
                    "topic": topic,
                    "analysis": analysis,
                    "articles": articles
                })
            except Exception as e:
                print(f"Error processing topic {topic}: {str(e)}")
                continue
            
        return newsletter_sections
    
    def format_newsletter(self, sections):
        """Format the newsletter content in markdown."""
        current_date = datetime.now().strftime("%B %d, %Y")
        
        newsletter_md = f"""
# AI Research Newsletter
## {current_date}

Dear Subscriber,

Here's your curated AI research update for today.

---
"""
        
        for section in sections:
            newsletter_md += f"""
## {section['topic']}

{section['analysis']}

### Featured Articles:
"""
            
            for article in section['articles']:
                newsletter_md += f"""
* [{article['title']}]({article['url']})
  * {article['summary'][:200]}...  # Limit summary length
"""
            
            newsletter_md += "\n---\n"
            
        newsletter_md += """
*This newsletter is generated by AI to help you stay updated with the latest developments.*
"""
        return newsletter_md
    
    def send_newsletter(self, newsletter_content, email_config):
        """Send the newsletter via email."""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"AI Research Newsletter - {datetime.now().strftime('%B %d, %Y')}"
        msg['From'] = email_config['from_email']
        msg['To'] = email_config['to_email']
        
        # Convert markdown to HTML
        html_content = markdown.markdown(newsletter_content)
        
        # Attach both plain text and HTML versions
        msg.attach(MIMEText(newsletter_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        # Send email
        with smtplib.SMTP_SSL(email_config['smtp_server'], email_config['smtp_port']) as server:
            server.login(email_config['username'], email_config['password'])
            server.send_message(msg)

    def save_newsletter(self, newsletter_content, filename=None):
        """Save the newsletter to a file."""
        if filename is None:
            filename = f"newsletter_{datetime.now().strftime('%Y%m%d')}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(newsletter_content)
        
        return filename 