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
import datetime

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
        self.reply_chains = {}  # Store conversation chains: {tweet_id: {'original_post': post_data, 'replies': [reply_data]}}
        self.bot_replies = set()  # Track tweet IDs of our own replies
        
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

    def reply_to_tweet(self, text: str, in_reply_to_tweet_id: str, original_post_id: str = None) -> bool:
        """Reply to a specific tweet."""
        try:
            logger.info(f"Replying to tweet {in_reply_to_tweet_id}: {text}")
            response = self.twitter_api.create_tweet(
                text=text,
                in_reply_to_tweet_id=in_reply_to_tweet_id
            )
            reply_id = response.data['id']
            logger.info(f"Successfully posted reply: {text}")
            logger.info(f"Reply Tweet ID: {reply_id}")

            # Track this as our reply
            self.bot_replies.add(reply_id)

            # If this is a reply to a popular post, track the conversation chain
            if original_post_id and self.config.get('track_reply_chains', False):
                if original_post_id not in self.reply_chains:
                    self.reply_chains[original_post_id] = {'replies': []}

                self.reply_chains[original_post_id]['replies'].append({
                    'id': reply_id,
                    'text': text,
                    'in_reply_to': in_reply_to_tweet_id,
                    'timestamp': datetime.datetime.now(datetime.timezone.utc),
                    'is_bot_reply': True
                })

            return True

        except Exception as e:
            logger.error(f"Error replying to tweet: {e}")
            return False

    def check_and_reply_to_mentions(self):
        """Check for new mentions and reply to them."""
        try:
            logger.info("Checking for new mentions...")

            # Get my user ID
            my_user_id = self.twitter_api.get_me().data.id

            # Get mentions using the correct API method
            mentions = self.twitter_api.get_users_mentions(
                id=my_user_id,
                since_id=self.last_mention_id,
                max_results=10,
                tweet_fields=['author_id', 'created_at', 'conversation_id'],
                expansions=['author_id'],
                user_fields=['username']
            )

            if not mentions.data:
                logger.info("No new mentions found")
                return

            logger.info(f"Found {len(mentions.data)} new mentions")

            # Create user mapping for usernames
            users_map = {}
            if mentions.includes and 'users' in mentions.includes:
                for user in mentions.includes['users']:
                    users_map[user.id] = user.username

            for mention in mentions.data:
                # Skip our own tweets
                if str(mention.author_id) == str(my_user_id):
                    continue

                logger.info(f"Processing mention from user {mention.author_id}: {mention.text}")

                # Generate a random fact reply
                fact = self.generate_random_fact_reply()
                if fact:
                    # Get the username of the person who mentioned us
                    username = users_map.get(mention.author_id, 'unknown')

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

    def get_popular_posts(self, username: str, max_results: int = 10) -> list:
        """Get popular posts from a specific Twitter account."""
        try:
            logger.info(f"Fetching popular posts from @{username}")

            # Get user ID from username
            user = self.twitter_api.get_user(username=username)
            if not user.data:
                logger.error(f"User @{username} not found")
                return []

            user_id = user.data.id

            # Calculate time threshold for recent posts
            import datetime
            hours_ago = self.config.get('popular_posts_max_age_hours', 24)
            time_threshold = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=hours_ago)

            # Get recent tweets from the user
            tweets = self.twitter_api.get_users_tweets(
                id=user_id,
                max_results=max_results * 2,  # Get more to filter by popularity
                tweet_fields=['created_at', 'public_metrics', 'author_id'],
                exclude=['retweets', 'replies']  # Only original tweets
            )

            if not tweets.data:
                logger.info(f"No tweets found for @{username}")
                return []

            # Filter and sort by popularity
            min_likes = self.config.get('popular_posts_min_likes', 1000)
            popular_posts = []

            for tweet in tweets.data:
                # Check if tweet is recent enough
                if tweet.created_at < time_threshold:
                    continue

                # Check if tweet has enough likes
                likes = tweet.public_metrics.get('like_count', 0)
                if likes >= min_likes:
                    popular_posts.append({
                        'id': tweet.id,
                        'text': tweet.text,
                        'likes': likes,
                        'retweets': tweet.public_metrics.get('retweet_count', 0),
                        'replies': tweet.public_metrics.get('reply_count', 0),
                        'created_at': tweet.created_at
                    })

            # Sort by likes (most popular first)
            popular_posts.sort(key=lambda x: x['likes'], reverse=True)

            # Limit to max_results
            popular_posts = popular_posts[:max_results]

            logger.info(f"Found {len(popular_posts)} popular posts from @{username}")
            return popular_posts

        except Exception as e:
            logger.error(f"Error fetching popular posts from @{username}: {e}")
            return []

    def get_popular_posts_from_all_users(self, max_results: int = 10) -> list:
        """Get popular posts from all users using search."""
        try:
            logger.info("Fetching popular posts from all users")

            # Get search keywords from config
            keywords = self.config.get('search_keywords', ['trending', 'viral', 'popular'])

            # Calculate time threshold for recent posts
            import datetime
            hours_ago = self.config.get('popular_posts_max_age_hours', 24)
            time_threshold = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=hours_ago)

            all_popular_posts = []

            # Search for each keyword
            for keyword in keywords:
                try:
                    logger.info(f"Searching for posts with keyword: {keyword}")

                    # Search for recent tweets with the keyword
                    search_query = f"{keyword} -is:retweet -is:reply lang:en"

                    tweets = self.twitter_api.search_recent_tweets(
                        query=search_query,
                        max_results=50,  # Get more to filter by popularity
                        tweet_fields=['created_at', 'public_metrics', 'author_id', 'lang'],
                        user_fields=['username', 'verified']
                    )

                    if not tweets.data:
                        logger.info(f"No tweets found for keyword: {keyword}")
                        continue

                    # Filter and collect popular posts
                    min_likes = self.config.get('popular_posts_min_likes', 1000)

                    for tweet in tweets.data:
                        # Check if tweet is recent enough
                        if tweet.created_at < time_threshold:
                            continue

                        # Check if tweet has enough likes
                        likes = tweet.public_metrics.get('like_count', 0)
                        if likes >= min_likes:
                            # Get author info if available
                            author_username = 'unknown'
                            if tweets.includes and 'users' in tweets.includes:
                                for user in tweets.includes['users']:
                                    if user.id == tweet.author_id:
                                        author_username = user.username
                                        break

                            all_popular_posts.append({
                                'id': tweet.id,
                                'text': tweet.text,
                                'likes': likes,
                                'retweets': tweet.public_metrics.get('retweet_count', 0),
                                'replies': tweet.public_metrics.get('reply_count', 0),
                                'created_at': tweet.created_at,
                                'author_id': tweet.author_id,
                                'author_username': author_username,
                                'keyword': keyword
                            })

                    # Add delay between keyword searches to avoid rate limiting
                    time.sleep(2)

                except Exception as e:
                    logger.error(f"Error searching for keyword '{keyword}': {e}")
                    continue

            # Remove duplicates (same tweet ID)
            seen_ids = set()
            unique_posts = []
            for post in all_popular_posts:
                if post['id'] not in seen_ids:
                    seen_ids.add(post['id'])
                    unique_posts.append(post)

            # Sort by likes (most popular first)
            unique_posts.sort(key=lambda x: x['likes'], reverse=True)

            # Limit to max_results
            popular_posts = unique_posts[:max_results]

            logger.info(f"Found {len(popular_posts)} popular posts from all users")
            return popular_posts

        except Exception as e:
            logger.error(f"Error fetching popular posts from all users: {e}")
            return []

    def interact_with_post(self, post: dict, interaction_types: list) -> bool:
        """Interact with a post (like, retweet, or reply)."""
        try:
            tweet_id = post['id']
            success_count = 0

            for interaction in interaction_types:
                try:
                    if interaction == 'like':
                        self.twitter_api.like(tweet_id)
                        logger.info(f"Liked tweet {tweet_id}")
                        success_count += 1

                    elif interaction == 'retweet':
                        self.twitter_api.retweet(tweet_id)
                        logger.info(f"Retweeted tweet {tweet_id}")
                        success_count += 1

                    elif interaction == 'reply':
                        # Generate a contextual reply
                        reply_text = self.generate_contextual_reply(post)
                        if reply_text:
                            # Store original post data for conversation tracking
                            if self.config.get('track_reply_chains', False):
                                if tweet_id not in self.reply_chains:
                                    self.reply_chains[tweet_id] = {
                                        'original_post': post,
                                        'replies': []
                                    }

                            self.reply_to_tweet(reply_text, tweet_id, original_post_id=tweet_id)
                            logger.info(f"Replied to tweet {tweet_id}: {reply_text}")
                            success_count += 1
                        else:
                            logger.error(f"Failed to generate reply for tweet {tweet_id}")

                    # Add delay between interactions to avoid rate limiting
                    time.sleep(2)

                except Exception as e:
                    logger.error(f"Error performing {interaction} on tweet {tweet_id}: {e}")

            return success_count > 0

        except Exception as e:
            logger.error(f"Error interacting with post {post.get('id', 'unknown')}: {e}")
            return False

    def generate_contextual_reply(self, post: dict) -> Optional[str]:
        """Generate a contextual reply to a popular post."""
        try:
            post_text = post.get('text', '')

            headers = {
                "Authorization": f"Bearer {self.config['openrouter_api_key']}",
                "Content-Type": "application/json"
            }

            prompt = f"""Generate a brief, engaging reply to this tweet in under 250 characters.
            Be conversational, relevant, and add value to the discussion. Don't just agree - provide insight, ask a thoughtful question, or share a related interesting fact.

            Tweet: "{post_text}"

            Reply:"""

            data = {
                "model": self.config.get('openrouter_model', 'anthropic/claude-3-haiku'),
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 100,
                "temperature": 0.7
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                reply = result['choices'][0]['message']['content'].strip()

                # Ensure it's under character limit
                if len(reply) > 250:
                    reply = reply[:247] + "..."

                logger.info(f"Generated contextual reply: {reply}")
                return reply
            else:
                logger.error(f"OpenRouter API error for contextual reply: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error generating contextual reply: {e}")
            return None

    def get_conversation_context(self, tweet_id: str) -> str:
        """Get the full conversation context for a tweet."""
        try:
            # Get the conversation thread
            conversation = self.twitter_api.get_tweets(
                ids=[tweet_id],
                tweet_fields=['conversation_id', 'in_reply_to_user_id', 'referenced_tweets'],
                expansions=['referenced_tweets.id', 'author_id'],
                user_fields=['username']
            )

            if not conversation.data:
                return ""

            tweet = conversation.data[0]
            conversation_id = tweet.conversation_id

            # Get all tweets in the conversation
            conversation_tweets = self.twitter_api.search_recent_tweets(
                query=f"conversation_id:{conversation_id}",
                max_results=100,
                tweet_fields=['created_at', 'author_id', 'in_reply_to_user_id', 'referenced_tweets'],
                expansions=['author_id'],
                user_fields=['username']
            )

            if not conversation_tweets.data:
                return ""

            # Build conversation context
            context_parts = []
            users_map = {}

            # Create user mapping
            if conversation_tweets.includes and 'users' in conversation_tweets.includes:
                for user in conversation_tweets.includes['users']:
                    users_map[user.id] = user.username

            # Sort tweets by creation time
            sorted_tweets = sorted(conversation_tweets.data, key=lambda x: x.created_at)

            for tweet in sorted_tweets:
                username = users_map.get(tweet.author_id, 'unknown')
                context_parts.append(f"@{username}: {tweet.text}")

            return "\n".join(context_parts[-10:])  # Last 10 tweets for context

        except Exception as e:
            logger.error(f"Error getting conversation context: {e}")
            return ""

    def generate_contextual_reply_with_thread(self, reply_tweet: dict, original_post: dict = None) -> Optional[str]:
        """Generate a contextual reply considering the full conversation thread."""
        try:
            reply_text = reply_tweet.get('text', '')

            # Get conversation context
            conversation_context = self.get_conversation_context(reply_tweet['id'])

            # Include original post context if available
            original_context = ""
            if original_post:
                original_context = f"Original post: {original_post.get('text', '')}\n\n"

            headers = {
                "Authorization": f"Bearer {self.config['openrouter_api_key']}",
                "Content-Type": "application/json"
            }

            prompt = f"""You are replying to a conversation thread. Generate a brief, engaging reply in under 250 characters.
            Be conversational, relevant, and add value to the discussion. Consider the full conversation context.

            {original_context}Conversation context:
            {conversation_context}

            Latest reply to respond to: "{reply_text}"

            Your reply:"""

            data = {
                "model": self.config.get('openrouter_model', 'anthropic/claude-3-haiku'),
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 100,
                "temperature": 0.7
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                reply = result['choices'][0]['message']['content'].strip()

                # Ensure it's under character limit
                if len(reply) > 250:
                    reply = reply[:247] + "..."

                logger.info(f"Generated thread-aware reply: {reply}")
                return reply
            else:
                logger.error(f"OpenRouter API error for thread reply: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error generating thread-aware reply: {e}")
            return None

    def check_for_replies_to_bot(self):
        """Check for replies to the bot's tweets and respond with context."""
        try:
            if not self.config.get('reply_to_replies', False):
                return

            logger.info("Checking for replies to bot's tweets...")

            # Get my user ID
            my_user_id = self.twitter_api.get_me().data.id

            # Get mentions that might be replies to our tweets
            mentions = self.twitter_api.get_users_mentions(
                id=my_user_id,
                since_id=self.last_mention_id,
                max_results=100,
                tweet_fields=['author_id', 'created_at', 'conversation_id', 'in_reply_to_user_id', 'referenced_tweets'],
                expansions=['referenced_tweets.id', 'author_id'],
                user_fields=['username']
            )

            if not mentions.data:
                logger.info("No new mentions found")
                return

            my_user_id_str = str(my_user_id)
            max_depth = self.config.get('max_reply_chain_depth', 5)

            for mention in mentions.data:
                # Skip our own tweets
                if str(mention.author_id) == my_user_id_str:
                    continue

                # Check if this is a reply to one of our replies
                if mention.referenced_tweets:
                    for ref_tweet in mention.referenced_tweets:
                        if ref_tweet.type == 'replied_to' and ref_tweet.id in self.bot_replies:
                            logger.info(f"Found reply to our tweet {ref_tweet.id}: {mention.text}")

                            # Find the original post this conversation started from
                            original_post = None
                            conversation_id = mention.conversation_id

                            for post_id, chain_data in self.reply_chains.items():
                                if post_id == conversation_id:
                                    original_post = chain_data.get('original_post')
                                    break

                            # Check conversation depth to avoid infinite loops
                            conversation_depth = len([r for r in self.reply_chains.get(conversation_id, {}).get('replies', []) if r.get('is_bot_reply')])

                            if conversation_depth >= max_depth:
                                logger.info(f"Max conversation depth ({max_depth}) reached for conversation {conversation_id}")
                                continue

                            # Generate contextual reply
                            reply_text = self.generate_contextual_reply_with_thread(
                                {'id': mention.id, 'text': mention.text},
                                original_post
                            )

                            if reply_text:
                                # Get the username of the person who replied
                                username = 'unknown'
                                if mentions.includes and 'users' in mentions.includes:
                                    for user in mentions.includes['users']:
                                        if user.id == mention.author_id:
                                            username = user.username
                                            break

                                # Create reply with username
                                full_reply = f"@{username} {reply_text}"

                                # Reply to the mention
                                success = self.reply_to_tweet(full_reply, mention.id, original_post_id=conversation_id)
                                if success:
                                    logger.info(f"Successfully replied to @{username} in conversation thread")
                                else:
                                    logger.error(f"Failed to reply to @{username} in conversation thread")
                            else:
                                logger.error("Failed to generate contextual thread reply")

                            break

                # Update last mention ID
                self.last_mention_id = mention.id

                # Add delay between replies
                time.sleep(3)

        except Exception as e:
            logger.error(f"Error checking for replies to bot: {e}")

    def check_and_interact_with_popular_posts(self):
        """Check for popular posts and interact with them."""
        try:
            if not self.config.get('interact_with_popular_posts', False):
                return

            search_all_users = self.config.get('search_all_users', False)

            if search_all_users:
                # Search for popular posts from all users
                logger.info("Checking popular posts from all users")
                popular_posts = self.get_popular_posts_from_all_users(max_results=5)
            else:
                # Search for popular posts from specific user
                target_username = self.config.get('target_twitter_username')
                if not target_username:
                    logger.warning("No target username specified for popular posts interaction")
                    return

                logger.info(f"Checking popular posts from @{target_username}")
                popular_posts = self.get_popular_posts(target_username, max_results=5)

            if not popular_posts:
                logger.info("No popular posts found to interact with")
                return

            # Get interaction settings
            interaction_types = self.config.get('popular_posts_interaction_types', ['like'])
            reply_to_all = self.config.get('popular_posts_reply_to_all', False)
            reply_chance = self.config.get('popular_posts_reply_chance', 0.3)

            for post in popular_posts:
                # Log post info with author if available
                author_info = f" by @{post.get('author_username', 'unknown')}" if search_all_users else ""
                keyword_info = f" (keyword: {post.get('keyword', 'N/A')})" if search_all_users else ""
                logger.info(f"Processing popular post{author_info}: {post['text'][:100]}... (Likes: {post['likes']}){keyword_info}")

                # Determine interactions for this post
                post_interactions = interaction_types.copy()

                # Handle reply logic
                if reply_to_all:
                    # Reply to ALL posts when reply_to_all is enabled
                    if 'reply' not in post_interactions:
                        post_interactions.append('reply')
                    logger.info("Will reply to this post (reply_to_all enabled)")
                else:
                    # Use chance-based reply system
                    if 'reply' not in post_interactions and random.random() < reply_chance:
                        post_interactions.append('reply')
                        logger.info(f"Will reply to this post (random chance: {reply_chance})")

                # Interact with the post
                success = self.interact_with_post(post, post_interactions)
                if success:
                    logger.info(f"Successfully interacted with popular post {post['id']}")
                else:
                    logger.error(f"Failed to interact with popular post {post['id']}")

                # Add delay between posts to avoid rate limiting
                time.sleep(5)

        except Exception as e:
            logger.error(f"Error checking and interacting with popular posts: {e}")

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
        reply_to_replies = self.config.get('reply_to_replies', False)
        interact_with_popular_posts = self.config.get('interact_with_popular_posts', False)
        popular_posts_interval = self.config.get('popular_posts_check_interval_hours', 6)
        search_all_users = self.config.get('search_all_users', False)
        target_username = self.config.get('target_twitter_username', 'unknown')

        # Log startup configuration
        log_message = f"Twitter bot started. Will post every 24 hours"
        if reply_to_mentions:
            log_message += f" and check mentions every {mention_interval} minutes"
        if reply_to_replies:
            log_message += f" and respond to replies to bot's tweets (with conversation context)"
        if interact_with_popular_posts:
            if search_all_users:
                keywords = self.config.get('search_keywords', ['trending'])
                log_message += f" and search for popular posts from all users (keywords: {', '.join(keywords)}) every {popular_posts_interval} hours"
            else:
                log_message += f" and check popular posts from @{target_username} every {popular_posts_interval} hours"

            if self.config.get('check_popular_posts_on_startup', True):
                log_message += " (including on startup)"
        log_message += "."
        logger.info(log_message)

        # Schedule the job to run every 24 hours
        schedule.every(24).hours.do(self.create_and_post_tweet)

        # Schedule mention checking if enabled
        if reply_to_mentions:
            schedule.every(mention_interval).minutes.do(self.check_and_reply_to_mentions)

        # Schedule reply-to-replies checking if enabled
        if self.config.get('reply_to_replies', False):
            schedule.every(mention_interval).minutes.do(self.check_for_replies_to_bot)

        # Schedule popular posts interaction if enabled
        if interact_with_popular_posts:
            schedule.every(popular_posts_interval).hours.do(self.check_and_interact_with_popular_posts)

        # Post immediately on startup (optional)
        if self.config.get('post_on_startup', False):
            logger.info("Posting initial tweet on startup")
            self.create_and_post_tweet()

        # Check mentions immediately on startup if enabled
        if reply_to_mentions:
            logger.info("Checking mentions on startup")
            self.check_and_reply_to_mentions()

        # Check for replies to bot immediately on startup if enabled
        if self.config.get('reply_to_replies', False):
            logger.info("Checking for replies to bot on startup")
            self.check_for_replies_to_bot()

        # Check popular posts immediately on startup if enabled
        if interact_with_popular_posts and self.config.get('check_popular_posts_on_startup', True):
            logger.info("Checking popular posts on startup")
            self.check_and_interact_with_popular_posts()

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
