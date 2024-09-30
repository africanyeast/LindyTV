import os
import json
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from utils.utils import *

class SubscriptionOperations:

    def save_subscriptions(self, username):
        try:
            
            # Initialize API parameters
            scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
            api_service_name = "youtube"
            api_version = "v3"
            client_secrets_file = "client_secret.json"

            # Check if client_secret.json exists
            if not os.path.exists(client_secrets_file):
                raise FileNotFoundError(f"Error: '{client_secrets_file}' file not found.")

            # Get credentials and create an API client
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                client_secrets_file, scopes
            )
            credentials = flow.run_local_server(port=8080)

            youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

            # Get user subscriptions
            subscriptions, tags = self.get_subscriptions(youtube)

            # Save fetched data into respective JSON files
            user_folder = self.create_user_folder(username)
            SAVE_JSON_FILE(os.path.join(user_folder, 'subscriptions.json'), subscriptions)
            SAVE_JSON_FILE(os.path.join(user_folder, 'tags.json'), tags)

            # Categorize subscriptions by tags
            #self.categorize_subscriptions(username)

        except FileNotFoundError as e:
            print(e)
        except googleapiclient.errors.HttpError as e:
            print(f"An API error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def get_subscriptions(self, youtube):
        """Fetch the list of subscriptions from YouTube."""
        subscriptions = []
        tags = []
        try:
            request = youtube.subscriptions().list(part="snippet", mine=True, maxResults=50)

            while request:
                response = request.execute()
                for item in response.get('items', []):
                    # Extract metadata for each channel
                    long_channel_info = {
                        'channel_id': item['snippet']['resourceId']['channelId'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'published_at': item['snippet']['publishedAt']
                    }
                    short_channel_info = {
                        'sub_id': item['snippet']['resourceId']['channelId'],
                        'title': item['snippet']['title'],
                        'tag': ""
                    }
                    subscriptions.append(long_channel_info)
                    tags.append(short_channel_info)

                request = youtube.subscriptions().list_next(request, response)

        except googleapiclient.errors.HttpError as e:
            print(f"Failed to fetch subscriptions: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while fetching subscriptions: {e}")

        return subscriptions, tags

    def categorize_subscriptions(self, username):
        """Categorize user subscriptions by tag and save as channels.json."""
        try:
            user_folder = GET_USER_FOLDER(username)
            subscriptions = LOAD_JSON_FILE(os.path.join(user_folder, 'tags.json'))

            if not subscriptions:
                print("No subscriptions data found.")
                return

            channels = {}
            for sub in subscriptions:
                tag = sub["tag"] or "Miscellaneous"
                if tag not in channels:
                    channels[tag] = {"subs": [], "channel_no": len(channels) + 1}
                channels[tag]["subs"].append({"id": sub["sub_id"], "title": sub["title"]})

            # Save categorized channels into a json file
            SAVE_JSON_FILE(os.path.join(user_folder, 'channels.json'), channels)
            print("Categorization complete. Result written to channels.json")

        except Exception as e:
            print(f"An error occurred during categorization: {e}")

    def create_user_folder(self, username):
        """Create a folder structure for the user based on their username."""
        base_folder = 'data'
        user_folder = os.path.join(base_folder, username)
        subfolders = ['playlists', 'videos']

        try:
            # Create user folder and subfolders if they don't exist
            os.makedirs(user_folder, exist_ok=True)
            print(f"Created or found folder for {username}")

            for subfolder in subfolders:
                os.makedirs(os.path.join(user_folder, subfolder), exist_ok=True)

            return user_folder

        except OSError as e:
            print(f"Error creating folder structure: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
