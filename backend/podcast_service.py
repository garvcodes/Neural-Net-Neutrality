"""
Podcast generation and management service.

Handles:
- Podcast script generation from articles
- Episode metadata management
- Article integration
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from openai import OpenAI
import os


class PodcastService:
    """Service for generating and managing podcasts"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"
    
    def create_news_prompt(self, articles: List[Dict]) -> str:
        """Format articles into a news anchor script prompt"""
        articles_text = ""
        for i, article in enumerate(articles, 1):
            source = article.get("source", "Unknown")
            content = article.get("content") or article.get("summary") or "No content available"
            
            articles_text += f"\nStory {i}: {article.get('title', 'Untitled')}"
            articles_text += f"\nSource: {source}"
            articles_text += f"\nContent: {content}\n---"
        
        prompt = f"""You are a professional news anchor creating a 2-3 minute broadcast script.

Create a politically neutral, natural and engaging news broadcast from these {len(articles)} top stories:
{articles_text}

Requirements:
- Start with a warm greeting and introduction (Your company: Neutral Network News)
- This is a monologue, so never label who is speaking (no "Anchor:" prefix)
- No settings or exposition (no music or technical cues)
- Present each story in a conversational, professional tone
- Use smooth transitions between stories
- Keep it concise but informative
- End with a brief closing statement about staying informed

The complete news script:"""
        
        return prompt
    
    def generate_script(self, articles: List[Dict], model: Optional[str] = None) -> str:
        """Generate news script using OpenAI GPT"""
        if not model:
            model = self.model
        
        prompt = self.create_news_prompt(articles)
        
        response = self.openai_client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional news anchor with years of experience in broadcast journalism. Create engaging, clear, and professional news scripts for a neutral news podcast."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    
    def estimate_duration(self, script: str) -> int:
        """Estimate podcast duration in seconds from script length"""
        # Rough estimate: ~150 words per minute at normal speaking speed
        word_count = len(script.split())
        duration_seconds = max(120, int(word_count / 150 * 60))  # Min 2 minutes
        return duration_seconds
    
    def format_episode(self, 
                      script: str, 
                      articles: List[Dict],
                      title: Optional[str] = None,
                      model: str = "gpt-4o-mini") -> Dict:
        """Format generated podcast into episode object"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        episode_id = f"episode_{timestamp}"
        
        word_count = len(script.split())
        duration = self.estimate_duration(script)
        
        return {
            "episode_id": episode_id,
            "title": title or f"Daily Brief - {datetime.now().strftime('%B %d, %Y')}",
            "description": "AI-generated neutral news podcast covering current events",
            "script": script,
            "duration_seconds": duration,
            "articles": articles,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "model": model,
                "word_count": word_count,
                "articles_count": len(articles),
                "voice": "news_anchor",
                "language": "en"
            }
        }
    
    def get_sample_articles(self) -> List[Dict]:
        """Return sample articles for testing"""
        return [
            {
                "id": 1,
                "title": "New AI Safety Framework Released",
                "content": "Leading AI researchers have released a comprehensive safety framework for large language models, emphasizing the importance of transparency and accountability in AI development.",
                "summary": "New guidelines for AI safety",
                "source": "AI Research Institute",
                "url": "https://example.com/1",
                "published_at": datetime.now().isoformat()
            },
            {
                "id": 2,
                "title": "Global Tech Companies Unite on AI Standards",
                "content": "Major technology companies announced they will adopt common safety standards for AI development, aiming to ensure responsible deployment of artificial intelligence systems.",
                "summary": "Tech companies collaborate on AI",
                "source": "TechNews Daily",
                "url": "https://example.com/2",
                "published_at": datetime.now().isoformat()
            },
            {
                "id": 3,
                "title": "Policy Debate Intensifies Over AI Regulation",
                "content": "Lawmakers from different parties discussed various approaches to regulating artificial intelligence development, with emphasis on balancing innovation with safety concerns.",
                "summary": "AI regulation discussion",
                "source": "Policy Watch",
                "url": "https://example.com/3",
                "published_at": datetime.now().isoformat()
            },
            {
                "id": 4,
                "title": "University Expands AI Research Programs",
                "content": "Leading universities announced expanded AI research initiatives with new funding to support cutting-edge research and development in artificial intelligence.",
                "summary": "Universities boost AI research",
                "source": "Education News",
                "url": "https://example.com/4",
                "published_at": datetime.now().isoformat()
            },
            {
                "id": 5,
                "title": "AI Impact Study Shows Mixed Results",
                "content": "A comprehensive new study examines the economic and social impacts of AI implementation, showing both opportunities and challenges for different sectors.",
                "summary": "Study on AI impacts",
                "source": "Research Foundation",
                "url": "https://example.com/5",
                "published_at": datetime.now().isoformat()
            }
        ]
    
    def get_sample_episodes(self, limit: int = 10) -> List[Dict]:
        """Return sample episodes for the podcast library"""
        episodes = []
        
        sample_titles = [
            "Daily Brief - October 26, 2025",
            "Daily Brief - October 25, 2025",
            "Daily Brief - October 24, 2025",
            "Daily Brief - October 23, 2025",
            "Daily Brief - October 22, 2025",
            "Daily Brief - October 21, 2025",
            "Daily Brief - October 20, 2025",
            "Daily Brief - October 19, 2025",
            "Daily Brief - October 18, 2025",
            "Daily Brief - October 17, 2025",
        ]
        
        for i, title in enumerate(sample_titles[:limit]):
            date_offset = i
            episode_date = (datetime.now() - timedelta(days=date_offset)).strftime("%Y-%m-%d")
            
            episode = {
                "id": f"episode_{i+1}",
                "title": title,
                "description": "Your daily AI-generated neutral news podcast covering the latest in AI and politics",
                "publication_date": episode_date,
                "audio_url": f"https://example.com/podcast_{i+1}.mp3",
                "duration_seconds": 180,
                "cover_image_url": "https://images.unsplash.com/photo-1478737270239-2f02b77fc618?w=800&q=80",
                "play_count": i * 50,
                "script_available": i < 3  # Only latest 3 have scripts
            }
            episodes.append(episode)
        
        return episodes


# Create singleton instance
podcast_service = PodcastService()
