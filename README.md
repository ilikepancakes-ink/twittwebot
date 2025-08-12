# Twitter Bot with OpenRouter API

A Python script that automatically posts AI-generated random statements to Twitter every 24 hours using the OpenRouter API for content generation.

## Features

- 🤖 AI-powered content generation using OpenRouter API
- 🐦 Automatic posting to Twitter
- ⏰ Scheduled posting every 24 hours
- 💬 Automatic replies to mentions with random facts
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
- Log all activities to `twitter_bot.log`
- Continue running until stopped with Ctrl+C

## Configuration Options

- `openrouter_model`: The AI model to use (default: "anthropic/claude-3-haiku")
- `post_on_startup`: Whether to post immediately when the bot starts (default: false)
- `reply_to_mentions`: Whether to automatically reply to mentions (default: true)
- `mention_check_interval_minutes`: How often to check for mentions in minutes (default: 5)

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
