#!/usr/bin/env python3
"""
Twitter Bot with OpenRouter API Integration
Automatically posts random AI-generated statements to Twitter every 24 hours.
"""

import time
import json
import logging
import schedule
import requests
import tweepy
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
        self.username = self.get_username()
        self.last_mention_id = None
        
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

    def get_username(self) -> str:
        """Get the authenticated user's username."""
        try:
            user = self.twitter_api.get_me()
            username = user.data.username
            logger.info(f"Authenticated as: @{username}")
            return username
        except Exception as e:
            logger.error(f"Failed to get username: {e}")
            return "unknown"
    
    def generate_random_statement(self) -> Optional[str]:
        """Generate a random statement using OpenRouter API."""
        try:
            # Random prompts for variety - focused on random facts
            prompts = [
                "Share a bizarre but true fact about animals in under 280 characters.",
                "Tell me a weird historical fact that sounds made up but isn't in under 280 characters.",
                "Share a strange fact about space or the universe in under 280 characters.",
                "Give me an odd fact about the human body in under 280 characters.",
                "Share a random fact about food or cooking that most people don't know in under 280 characters.",
                "Tell me a weird fact about technology or inventions in under 280 characters.",
                "Share a bizarre fact about nature or weather in under 280 characters.",
                "Give me a random fact about a country or culture in under 280 characters.",
                "Share an odd fact about language or words in under 280 characters.",
                "Tell me a strange fact about the ocean or marine life in under 280 characters."
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

    def generate_random_fact_reply(self) -> Optional[str]:
        """Generate a random fact for replying to mentions."""
        try:
            # Prompts specifically for replies - more conversational
            reply_prompts = [
                "Share a fun random fact in under 250 characters (leaving room for @username).",
                "Tell me something weird but true in under 250 characters.",
                "Give me a bizarre fact that will surprise someone in under 250 characters.",
                "Share an odd fact about animals, space, history, or science in under 250 characters.",
                "Tell me something random and interesting in under 250 characters."
            ]

            selected_prompt = random.choice(reply_prompts)

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
                "temperature": 0.9
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                fact = result['choices'][0]['message']['content'].strip()

                # Ensure it's under character limit (leaving room for @username)
                if len(fact) > 250:
                    fact = fact[:247] + "..."

                logger.info(f"Generated reply fact: {fact}")
                return fact
            else:
                logger.error(f"OpenRouter API error for reply: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error generating reply fact: {e}")
            return None

    def post_to_twitter(self, text: str) -> bool:
        """Post text to Twitter."""
        try:
            logger.info(f"Posting tweet as @{self.username}: {text}")
            response = self.twitter_api.create_tweet(text=text)
            logger.info(f"Successfully posted tweet: {text}")
            logger.info(f"Tweet ID: {response.data['id']}")
            return True

        except Exception as e:
            logger.error(f"Error posting to Twitter: {e}")
            return False

    def reply_to_tweet(self, text: str, in_reply_to_tweet_id: str) -> bool:
        """Reply to a specific tweet."""
        try:
            logger.info(f"Replying to tweet {in_reply_to_tweet_id}: {text}")
            response = self.twitter_api.create_tweet(
                text=text,
                in_reply_to_tweet_id=in_reply_to_tweet_id
            )
            logger.info(f"Successfully posted reply: {text}")
            logger.info(f"Reply Tweet ID: {response.data['id']}")
            return True

        except Exception as e:
            logger.error(f"Error replying to tweet: {e}")
            return False

    def check_and_reply_to_mentions(self):
        """Check for new mentions and reply to them."""
        try:
            logger.info("Checking for new mentions...")

            # Get mentions
            mentions = self.twitter_api.get_mentions(
                since_id=self.last_mention_id,
                max_results=10,
                tweet_fields=['author_id', 'created_at', 'conversation_id']
            )

            if not mentions.data:
                logger.info("No new mentions found")
                return

            logger.info(f"Found {len(mentions.data)} new mentions")

            for mention in mentions.data:
                # Skip our own tweets
                if str(mention.author_id) == str(self.twitter_api.get_me().data.id):
                    continue

                logger.info(f"Processing mention from user {mention.author_id}: {mention.text}")

                # Generate a random fact reply
                fact = self.generate_random_fact_reply()
                if fact:
                    # Get the username of the person who mentioned us
                    user = self.twitter_api.get_user(id=mention.author_id)
                    username = user.data.username

                    # Create reply with username
                    reply_text = f"@{username} {fact}"

                    # Reply to the mention
                    success = self.reply_to_tweet(reply_text, mention.id)
                    if success:
                        logger.info(f"Successfully replied to @{username}")
                    else:
                        logger.error(f"Failed to reply to @{username}")
                else:
                    logger.error("Failed to generate fact for reply")

                # Update last mention ID
                self.last_mention_id = mention.id

                # Add a small delay between replies to avoid rate limiting
                time.sleep(2)

        except Exception as e:
            logger.error(f"Error checking mentions: {e}")

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
        """Run the bot with 24-hour scheduling and optional mention checking."""
        mention_interval = self.config.get('mention_check_interval_minutes', 5)
        reply_to_mentions = self.config.get('reply_to_mentions', True)

        if reply_to_mentions:
            logger.info(f"Twitter bot started. Will post every 24 hours and check mentions every {mention_interval} minutes.")
        else:
            logger.info("Twitter bot started. Will post every 24 hours. Mention replies are disabled.")

        # Schedule the job to run every 24 hours
        schedule.every(24).hours.do(self.create_and_post_tweet)

        # Schedule mention checking if enabled
        if reply_to_mentions:
            schedule.every(mention_interval).minutes.do(self.check_and_reply_to_mentions)

        # Post immediately on startup (optional)
        if self.config.get('post_on_startup', False):
            logger.info("Posting initial tweet on startup")
            self.create_and_post_tweet()

        # Check mentions immediately on startup if enabled
        if reply_to_mentions:
            logger.info("Checking mentions on startup")
            self.check_and_reply_to_mentions()

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
