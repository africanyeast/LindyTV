import os
from dotenv import load_dotenv
load_dotenv()
user = os.getenv('USER_NAME')

# Create a new user subscription
# from subscriptions import SubscriptionOperations
# operation = SubscriptionOperations()
# operation.save_subscriptions(user)


# Create channels from user subscription
# from subscriptions import SubscriptionOperations
# operation = SubscriptionOperations()
# operation.categorize_subscriptions(user)


# Save videos from users sub channels
# from channels import ChannelOperations
# yt_api_key = os.getenv('YOUTUBE_API_KEY')
# operation = ChannelOperations(yt_api_key)
# operation.save_videos(user)

# Update playlist for user
# from channels import ChannelOperations
# yt_api_key = os.getenv('YOUTUBE_API_KEY')
# operation = ChannelOperations(yt_api_key)
# operation.update_playlist(user)