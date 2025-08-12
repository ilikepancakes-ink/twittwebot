#!/usr/bin/env python3
"""
Twitter Bot with OpenRouter API Integration
Automatically posts random AI-generated statements to Twitter every 24 hours.
"""

import os
import time
import json
import logging
import schedule
import requests
import tweepy
from datetime import datetime
from typing import Optional
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('twitter_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TwitterBot:
    def __init__(self, config_file: str = 'config.json'):
        """Initialize the Twitter bot with configuration."""
        self.config = self.load_config(config_file)
        self.twitter_api = self.setup_twitter_api()
        
    def load_config(self, config_file: str) -> dict:
        """Load configuration from JSON file."""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Validate required keys
            required_keys = [
                'openrouter_api_key',
                'twitter_bearer_token',
                'twitter_consumer_key',
                'twitter_consumer_secret',
                'twitter_access_token',
                'twitter_access_token_secret'
            ]
            
            for key in required_keys:
                if key not in config:
                    raise ValueError(f"Missing required configuration key: {key}")
            
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file {config_file} not found")
            raise
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in configuration file {config_file}")
            raise
    
    def setup_twitter_api(self) -> tweepy.Client:
        """Setup Twitter API client."""
        try:
            client = tweepy.Client(
                bearer_token=self.config['twitter_bearer_token'],
                consumer_key=self.config['twitter_consumer_key'],
                consumer_secret=self.config['twitter_consumer_secret'],
                access_token=self.config['twitter_access_token'],
                access_token_secret=self.config['twitter_access_token_secret'],
                wait_on_rate_limit=True
            )
            
            # Test the connection
            client.get_me()
            logger.info("Twitter API connection established successfully")
            return client
            
        except Exception as e:
            logger.error(f"Failed to setup Twitter API: {e}")
            raise
    
    def generate_random_statement(self) -> Optional[str]:
        """Generate a random statement using OpenRouter API."""
        try:
            # Random prompts for variety
            prompts = [
                "Generate a thought-provoking statement about technology and society in under 280 characters.",
                "Create an inspiring quote about creativity and innovation in under 280 characters.",
                "Write a philosophical observation about human nature in under 280 characters.",
                "Generate a witty observation about modern life in under 280 characters.",
                "Create a motivational statement about personal growth in under 280 characters.",
                "Write an interesting fact or insight about science in under 280 characters.",
                "Generate a humorous but insightful comment about daily life in under 280 characters."
            ]
            
            selected_prompt = random.choice(prompts)
            
            headers = {
                "Authorization": f"Bearer {self.config['openrouter_api_key']}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.config.get('openrouter_model', 'anthropic/claude-3-haiku'),
                "messages": [
                    {
                        "role": "user",
                        "content": selected_prompt
                    }
                ],
                "max_tokens": 100,
                "temperature": 0.8
            }
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                statement = result['choices'][0]['message']['content'].strip()
                
                # Ensure it's under Twitter's character limit
                if len(statement) > 280:
                    statement = statement[:277] + "..."
                
                logger.info(f"Generated statement: {statement}")
                return statement
            else:
                logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating statement: {e}")
            return None
    
    def post_to_twitter(self, text: str) -> bool:
        """Post text to Twitter."""
        try:
            response = self.twitter_api.create_tweet(text=text)
            logger.info(f"Successfully posted tweet: {text}")
            logger.info(f"Tweet ID: {response.data['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error posting to Twitter: {e}")
            return False
    
    def create_and_post_tweet(self):
        """Generate a statement and post it to Twitter."""
        logger.info("Starting tweet generation and posting process")
        
        statement = self.generate_random_statement()
        if statement:
            success = self.post_to_twitter(statement)
            if success:
                logger.info("Tweet posted successfully!")
            else:
                logger.error("Failed to post tweet")
        else:
            logger.error("Failed to generate statement")
    
    def run_scheduler(self):
        """Run the bot with 24-hour scheduling."""
        logger.info("Twitter bot started. Will post every 24 hours.")
        
        # Schedule the job to run every 24 hours
        schedule.every(24).hours.do(self.create_and_post_tweet)
        
        # Post immediately on startup (optional)
        if self.config.get('post_on_startup', False):
            logger.info("Posting initial tweet on startup")
            self.create_and_post_tweet()
        
        # Keep the script running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

def main():
    """Main function to run the Twitter bot."""
    try:
        bot = TwitterBot()
        bot.run_scheduler()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        raise

if __name__ == "__main__":
    main()
