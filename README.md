# Twitter Bot with OpenRouter API

A Python script that automatically posts AI-generated random statements to Twitter every 24 hours using the OpenRouter API for content generation.

## Features

- 🤖 AI-powered content generation using OpenRouter API
- 🐦 Automatic posting to Twitter
- ⏰ Scheduled posting every 24 hours
- 💬 Automatic replies to mentions with random facts
- 🔥 Interaction with popular posts from target accounts (like, retweet, reply)
- 🎯 Configurable popularity thresholds and interaction types
- 🧵 Conversation thread tracking and contextual replies to replies
- 🔄 Automatic responses to anyone who replies to the bot's tweets
- 📝 Variety of random fact prompts for diverse content
- 📊 Comprehensive logging
- ⚙️ Configurable settings

## Prerequisites

1. **Python 3.7+** installed on your system
2. **OpenRouter API account** - Sign up at [openrouter.ai](https://openrouter.ai)
3. **Twitter Developer account** - Apply at [developer.twitter.com](https://developer.twitter.com)

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get OpenRouter API Key

1. Go to [openrouter.ai](https://openrouter.ai)
2. Sign up for an account
3. Navigate to your API keys section
4. Create a new API key
5. Copy the API key for later use

### 3. Get Twitter API Credentials

1. Go to [developer.twitter.com](https://developer.twitter.com)
2. Apply for a developer account
3. Create a new app in the Twitter Developer Portal
4. Generate the following credentials:
   - Bearer Token
   - Consumer Key (API Key)
   - Consumer Secret (API Secret)
   - Access Token
   - Access Token Secret

**Important**: Make sure your Twitter app has **Read and Write** permissions to post tweets.

### 4. Configure the Bot

1. Copy the configuration template:
   ```bash
   cp config.json.template config.json
   ```

2. Edit `config.json` with your API credentials:
   ```json
   {
     "openrouter_api_key": "your_openrouter_api_key_here",
     "openrouter_model": "anthropic/claude-3-haiku",
     "twitter_bearer_token": "your_twitter_bearer_token_here",
     "twitter_consumer_key": "your_twitter_consumer_key_here",
     "twitter_consumer_secret": "your_twitter_consumer_secret_here",
     "twitter_access_token": "your_twitter_access_token_here",
     "twitter_access_token_secret": "your_twitter_access_token_secret_here",
     "post_on_startup": false,
     "reply_to_mentions": true,
     "mention_check_interval_minutes": 5
   }
   ```

### 5. Run the Bot

```bash
python twitter_bot.py
```

The bot will:
- Start immediately and log its status
- Post a tweet every 24 hours
- Check for mentions every 5 minutes and reply with random facts
- Interact with popular posts from target accounts (if enabled)
- Log all activities to `twitter_bot.log`
- Continue running until stopped with Ctrl+C

## Configuration Options

### Basic Settings
- `openrouter_model`: The AI model to use (default: "anthropic/claude-3-haiku")
- `post_on_startup`: Whether to post immediately when the bot starts (default: false)
- `check_popular_posts_on_startup`: Whether to check for popular posts immediately on startup (default: true)
- `reply_to_mentions`: Whether to automatically reply to mentions (default: true)
- `mention_check_interval_minutes`: How often to check for mentions in minutes (default: 5)

### Popular Posts Interaction Settings
- `interact_with_popular_posts`: Enable interaction with popular posts (default: false)
- `search_all_users`: Search for popular posts from all users instead of a specific account (default: false)
- `target_twitter_username`: Username of the account to monitor for popular posts (e.g., "elonmusk") - only used when `search_all_users` is false
- `search_keywords`: List of keywords to search for when `search_all_users` is true (default: ["trending", "viral", "popular"])
- `popular_posts_check_interval_hours`: How often to check for popular posts in hours (default: 6)
- `popular_posts_interaction_types`: Types of interactions to perform (default: ["like", "retweet"])
  - Available options: "like", "retweet", "reply"
- `popular_posts_min_likes`: Minimum number of likes for a post to be considered popular (default: 1000)
- `popular_posts_max_age_hours`: Maximum age of posts to consider in hours (default: 24)
- `popular_posts_reply_to_all`: Reply to ALL popular posts found (overrides reply_chance when true, default: false)
- `popular_posts_reply_chance`: Probability of replying to a popular post when reply_to_all is false (0.0-1.0, default: 0.3)

### Conversation Thread Settings
- `track_reply_chains`: Track conversation threads for contextual responses (default: false)
- `reply_to_replies`: Automatically respond to anyone who replies to the bot's tweets (default: false)
- `max_reply_chain_depth`: Maximum number of bot replies allowed in a single conversation thread (default: 5)

## Popular Posts Interaction

The bot can automatically interact with popular posts either from a specific Twitter account or from all users based on keywords. Here's how it works:

### Two Search Modes:

#### 1. Specific User Mode (`search_all_users`: false)
- **Monitoring**: The bot periodically checks the target account for recent posts
- **Filtering**: Posts are filtered based on popularity and age criteria
- **Best for**: Following specific influencers or accounts

#### 2. All Users Mode (`search_all_users`: true)
- **Searching**: The bot searches Twitter for posts containing specified keywords
- **Filtering**: Posts are filtered based on popularity, age, and language (English only)
- **Best for**: Finding trending content across all of Twitter

### Common Features:
1. **Filtering**: Posts are filtered based on:
   - Minimum number of likes (`popular_posts_min_likes`)
   - Maximum age (`popular_posts_max_age_hours`)
   - Only original tweets (no retweets or replies)
2. **Ranking**: Posts are ranked by popularity (like count)
3. **Interaction**: The bot can perform various interactions:
   - **Like**: Automatically likes popular posts
   - **Retweet**: Shares popular posts to your timeline
   - **Reply**: Generates contextual AI replies to popular posts
4. **Rate Limiting**: Built-in delays prevent hitting Twitter's rate limits

### Example Configurations

#### For Specific User:
```json
{
  "interact_with_popular_posts": true,
  "search_all_users": false,
  "target_twitter_username": "elonmusk",
  "popular_posts_check_interval_hours": 6,
  "popular_posts_interaction_types": ["like", "retweet"],
  "popular_posts_min_likes": 5000,
  "popular_posts_max_age_hours": 12,
  "popular_posts_reply_chance": 0.2
}
```

#### For All Users (Keyword Search) - Reply to ALL:
```json
{
  "interact_with_popular_posts": true,
  "search_all_users": true,
  "search_keywords": ["AI", "technology", "innovation", "startup", "crypto"],
  "popular_posts_check_interval_hours": 24,
  "check_popular_posts_on_startup": true,
  "popular_posts_interaction_types": ["like", "retweet", "reply"],
  "popular_posts_min_likes": 1000,
  "popular_posts_max_age_hours": 24,
  "popular_posts_reply_to_all": true
}
```

#### For All Users (Keyword Search) - Chance-based Replies:
```json
{
  "interact_with_popular_posts": true,
  "search_all_users": true,
  "search_keywords": ["AI", "technology", "innovation", "startup", "crypto"],
  "popular_posts_check_interval_hours": 24,
  "check_popular_posts_on_startup": true,
  "popular_posts_interaction_types": ["like"],
  "popular_posts_min_likes": 1000,
  "popular_posts_max_age_hours": 24,
  "popular_posts_reply_to_all": false,
  "popular_posts_reply_chance": 0.3
}
```

The first configuration will:
- Search for posts containing AI, technology, innovation, startup, or crypto keywords **every 24 hours** (and on startup)
- Like, retweet, and **reply to ALL** posts with 1000+ likes from the last 24 hours
- Generate AI-powered contextual responses for every popular post found

The second configuration will:
- Search for posts containing the same keywords **every 24 hours** (and on startup)
- Like posts with 1000+ likes from the last 24 hours
- Reply to only 30% of popular posts (randomly selected)

## ⚠️ Important Notes for Reply-to-All Feature

When using `"popular_posts_reply_to_all": true`, the bot will reply to **EVERY** popular post it finds. Consider these recommendations:

1. **Start with higher thresholds**: Use higher values for `popular_posts_min_likes` (e.g., 5000+) to limit the number of posts
2. **Longer intervals**: Use longer `popular_posts_check_interval_hours` (e.g., 12-24 hours) to avoid overwhelming activity
3. **Monitor rate limits**: Twitter has rate limits for posting - the bot includes delays but monitor your usage
4. **Quality keywords**: Use specific, relevant keywords to ensure you're replying to posts in your area of interest
5. **Test first**: Start with `popular_posts_reply_to_all: false` and a low `reply_chance` to test the system

### Recommended Safe Configuration for Reply-to-All:
```json
{
  "popular_posts_min_likes": 5000,
  "popular_posts_max_age_hours": 24,
  "popular_posts_check_interval_hours": 24,
  "check_popular_posts_on_startup": true,
  "search_keywords": ["specific", "relevant", "keywords"],
  "popular_posts_reply_to_all": true
}
```

## 🧵 Conversation Thread Tracking

The bot can track conversation threads and respond contextually to replies. Here's how it works:

### How Conversation Tracking Works:
1. **Initial Reply**: When the bot replies to a popular post, it stores the conversation context
2. **Reply Detection**: The bot monitors mentions to detect when someone replies to its tweets
3. **Context Gathering**: When a reply is detected, the bot gathers the full conversation thread
4. **Contextual Response**: The bot generates a response considering:
   - The original post that started the conversation
   - All previous messages in the thread
   - The specific reply it's responding to
5. **Depth Limiting**: Prevents infinite loops with `max_reply_chain_depth`

### Example Conversation Flow:
```
Original Post: "AI will revolutionize healthcare in the next decade"
Bot Reply: "Absolutely! AI diagnostics are already showing 95% accuracy rates..."
User Reply: "What about privacy concerns with medical AI?"
Bot Response: "Great point! Given the healthcare context we're discussing, privacy is crucial. Medical AI systems need robust encryption and patient consent frameworks..."
```

### Configuration for Conversation Tracking:
```json
{
  "track_reply_chains": true,
  "reply_to_replies": true,
  "max_reply_chain_depth": 5,
  "popular_posts_reply_to_all": true
}
```

This enables:
- Full conversation context in replies
- Automatic responses to anyone who engages with the bot
- Prevention of overly long conversation chains
- Contextual understanding spanning multiple exchanges

## Available OpenRouter Models

You can change the model in `config.json`. Popular options include:
- `anthropic/claude-3-haiku` (fast and cost-effective)
- `anthropic/claude-3-sonnet` (balanced performance)
- `openai/gpt-3.5-turbo` (OpenAI's model)
- `openai/gpt-4` (more advanced but costlier)

## Content Types

The bot generates various types of random facts:
- Bizarre but true facts about animals
- Weird historical facts
- Strange facts about space and the universe
- Odd facts about the human body
- Random facts about food and cooking
- Weird facts about technology and inventions
- Bizarre facts about nature and weather
- Random facts about countries and cultures
- Odd facts about language and words
- Strange facts about the ocean and marine life

When replying to mentions, the bot provides conversational random facts tailored for responses.

## Running as a Service

### On Linux (systemd)

1. Create a service file:
   ```bash
   sudo nano /etc/systemd/system/twitter-bot.service
   ```

2. Add the following content:
   ```ini
   [Unit]
   Description=Twitter Bot with OpenRouter API
   After=network.target

   [Service]
   Type=simple
   User=your_username
   WorkingDirectory=/path/to/your/bot
   ExecStart=/usr/bin/python3 /path/to/your/bot/twitter_bot.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start the service:
   ```bash
   sudo systemctl enable twitter-bot.service
   sudo systemctl start twitter-bot.service
   ```

### On Windows

Use Task Scheduler to run the script automatically on system startup.

## Troubleshooting

### Common Issues

1. **"Invalid credentials"**: Double-check your API keys in `config.json`
2. **"Rate limit exceeded"**: The bot handles rate limits automatically
3. **"Permission denied"**: Ensure your Twitter app has Read and Write permissions
4. **"Module not found"**: Run `pip install -r requirements.txt`

### Logs

Check `twitter_bot.log` for detailed information about the bot's activities and any errors.

## Security Notes

- Never commit `config.json` to version control
- Keep your API keys secure and private
- Consider using environment variables for production deployments
- Regularly rotate your API keys

## License

This project is open source. Feel free to modify and distribute as needed.

## Support

If you encounter issues:
1. Check the logs in `twitter_bot.log`
2. Verify your API credentials
3. Ensure your internet connection is stable
4. Check the OpenRouter and Twitter API status pages
