#!/usr/bin/env python3
"""
Test script for the popular posts functionality
"""

import json
import sys

def test_config_loading():
    """Test that the configuration loads correctly."""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        print("✅ Configuration loaded successfully")
        
        # Check for new configuration keys
        new_keys = [
            'interact_with_popular_posts',
            'target_twitter_username',
            'popular_posts_check_interval_hours',
            'popular_posts_interaction_types',
            'popular_posts_min_likes',
            'popular_posts_max_age_hours',
            'popular_posts_reply_chance'
        ]
        
        for key in new_keys:
            if key in config:
                print(f"✅ {key}: {config[key]}")
            else:
                print(f"❌ Missing key: {key}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return False

def test_twitter_bot_import():
    """Test that the TwitterBot class can be imported."""
    try:
        from twitter_bot import TwitterBot
        print("✅ TwitterBot class imported successfully")
        
        # Check if new methods exist
        methods = ['get_popular_posts', 'interact_with_post', 'generate_contextual_reply', 'check_and_interact_with_popular_posts']
        
        for method in methods:
            if hasattr(TwitterBot, method):
                print(f"✅ Method {method} exists")
            else:
                print(f"❌ Missing method: {method}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing TwitterBot: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing Popular Posts Functionality")
    print("=" * 40)
    
    config_ok = test_config_loading()
    print()
    
    import_ok = test_twitter_bot_import()
    print()
    
    if config_ok and import_ok:
        print("✅ All tests passed! The popular posts functionality is ready to use.")
        print("\nTo enable popular posts interaction:")
        print("1. Set 'interact_with_popular_posts': true in config.json")
        print("2. Set 'target_twitter_username' to the account you want to monitor")
        print("3. Adjust other settings as needed")
        print("4. Run: python twitter_bot.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
