import random
from datetime import timedelta, datetime
import json
from googleapiclient.discovery import build
import isodate
import math
from utils.utils import *
import os


class ChannelOperations:
    def __init__(self, api_key):
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def save_videos(self, username):
        """
        This method handle all the steps to save videos for each channel.
        """

        user_folder = GET_USER_FOLDER(username)

        data = LOAD_JSON_FILE(os.path.join(user_folder, 'channels.json'))

        # loop through each channel and its sub channels
        for channel_name, channel_info in data.items():
            print(f"Channel: {channel_name}")

            # Loop through each sub channel's ID in the current Channel
            for sub_channel in channel_info.get("subs", []):
                sub_channel_id = sub_channel.get("id")
                sub_channel_title = sub_channel.get("title")
                print(f"Sub Channel: {sub_channel_title}")
                if sub_channel_id:
                    try:
                        # tries to get the upload playlistID for a particular YouTube channel (sub channel in our context)
                        sub_channel_playlist_id = self.get_channel_uploads_playlist_id(sub_channel_id)
                        # tries to get all the videos for a particular YouTube channel using the upload playlistID
                        sub_channel_videos = self.get_channel_videos_from_playlist(sub_channel_playlist_id)
                        # tries to save all the videos for a particular YouTube channel into a JSON file
                        SAVE_JSON_FILE(os.path.join(user_folder, f"videos/{sub_channel_id}.json"), sub_channel_videos)
                    except Exception as e:
                        print(f"Error processing channel {sub_channel_id}: {e}")

    def get_channel_videos_from_playlist(self, playlist_id):
        videos = []
        video_ids = []
        video_titles = {}

        try:
            # initial request for playlist items
            request = self.youtube.playlistItems().list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=50
            )

            while request:
                response = request.execute()

                for item in response.get('items', []):
                    video_id = item['snippet']['resourceId']['videoId']
                    title = item['snippet']['title']
                    video_ids.append(video_id)
                    video_titles[video_id] = title

                # get the next page request, if available
                request = self.youtube.playlistItems().list_next(request, response)

            # fetch durations for all video IDs in the playlist
            durations = self.get_video_durations(video_ids)

            # filter out videos that are YouTube Shorts (duration <= 60 seconds)
            for video_id in video_ids:
                duration = durations.get(video_id, 0)
                if duration > 60:  # keep only videos longer than 60 seconds, discard YouTube shorts.
                    video_data = {
                        'id': video_id,
                        'title': video_titles.get(video_id, ''),
                        'duration': duration
                    }
                    videos.append(video_data)

        except Exception as e:
            print(f"Error fetching videos from playlist {playlist_id}: {e}")

        return videos


    def get_channel_uploads_playlist_id(self, channel_id):
        try:
            request = self.youtube.channels().list(
                part="contentDetails",
                id=channel_id
            )
            response = request.execute()
            return response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        except IndexError:
            print(f"Error: No uploads playlist found for channel ID {channel_id}.")
            return None
        except Exception as e:
            print(f"Error fetching uploads playlist for channel ID {channel_id}: {e}")
            return None

    def get_video_durations(self, video_ids):
        durations = {}
        # split the video_ids list into chunks of 50 (maximum allowed per request)
        chunk_size = 50
        total_batches = math.ceil(len(video_ids) / chunk_size)

        for i in range(total_batches):
            chunk = video_ids[i * chunk_size: (i + 1) * chunk_size]

            try:
                request = self.youtube.videos().list(
                    part="contentDetails",
                    id=','.join(chunk),
                    maxResults=chunk_size
                )
                response = request.execute()

                for item in response.get('items', []):
                    video_id = item['id']
                    duration_iso = item['contentDetails']['duration']
                    # parse ISO 8601 duration and convert to seconds
                    duration = isodate.parse_duration(duration_iso).total_seconds()
                    durations[video_id] = duration

            except Exception as e:
                print(f"Error fetching durations for video IDs {chunk}: {e}")

        return durations


    def create_channel_schedule(self, videos):
        TOTAL_TIME = 24 * 60 * 60  # total time slot for a 24-hour period in seconds

        try:
            if not isinstance(videos, list) or not all(isinstance(video, dict) for video in videos):
                raise ValueError("Videos should be a list of dictionaries.")

            schedule = []
            current_total_time = 0
            start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

            while current_total_time < TOTAL_TIME:
                random.shuffle(videos)
                video_added = False

                for video in videos:
                    if current_total_time + video['duration'] <= TOTAL_TIME:
                        play_at = start_time + timedelta(seconds=current_total_time)

                        schedule.append({
                            "id": video["id"],
                            "playAt": int(play_at.timestamp()),  # convert to unix timestamp
                            "duration": video['duration']
                        })

                        current_total_time += video['duration']
                        video_added = True

                    else:
                        break

                if not video_added:
                    break

            return schedule

        except Exception as e:
            print(f"Error creating schedule: {e}")
            return []


    def update_playlist(self, username):
        """
        This method handle all the steps to fetch data, schedule videos, and update the playlist.
        """
        try:
            # fetch all available channels
            user_folder = GET_USER_FOLDER(username)
            data = LOAD_JSON_FILE(os.path.join(user_folder, 'channels.json'))

            # Process each channel's videos and schedule them
            for channel_name, channel_info in data.items():
                try:
                    channel_videos = self.get_channel_videos(username, channel_info['subs'])
                    # Create schedule for the channel
                    videos_schedule = self.create_channel_schedule(channel_videos)
                    channel_no = channel_info.get('channel_no')

                    # Update playlist with the schedule for the current channel
                    self.update_channel_playlist(username, channel_name, channel_no, videos_schedule)
                
                except Exception as e:
                    print(f"Error processing channel {channel_name}: {e}")

        except Exception as e:
            print(f"Error processing channels: {e}")

    

    def get_channel_videos(self, username, sub_channels):
        channel_videos = []
        user_folder = GET_USER_FOLDER(username)
        # loop through each sub channel's ID for the sub channel details
        for sub_channel in sub_channels:
            sub_channel_id = sub_channel.get("id")
            sub_channel_title = sub_channel.get("title")
            # get all the videos stored for the sub channel
            sub_channel_videos = LOAD_JSON_FILE(os.path.join(user_folder, f"videos/{sub_channel_id}.json"))
            # Add all sub channel videos to the channel videos list
            channel_videos.extend(sub_channel_videos)
        return channel_videos


    def update_channel_playlist(self, username, channel_name, channel_no, schedule):
        try:
            # get the current date in the format YYYY-MM-DD
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            # generate the playlist file name using the current date
            playlist_filename = f'data/{username}/playlists/playlist-{current_date}.json'

            # try to open the file or create it if it doesn't exist
            try:
                with open(playlist_filename, 'r') as file:
                    content = file.read().strip()
                    if content:
                        playlist = json.loads(content)
                    else:
                        playlist = {}
            except json.JSONDecodeError:
                print("Error: The playlist file contains invalid JSON. Initializing with an empty playlist.")
                playlist = {}
            except FileNotFoundError:
                print(f"Playlist file for {current_date} not found. Creating a new playlist.")
                playlist = {}

            # Convert channel to string to ensure consistency
            channel = str(channel_no)

            # Update the schedule for the specified channel
            playlist[channel] = schedule

            # Write the updated playlist back to the file
            with open(playlist_filename, 'w') as file:
                json.dump(playlist, file, indent=4)

            print(f"Playlist updated for channel {channel_name} on {current_date}.")

        except Exception as e:
            print(f"Error updating playlist for {channel_name}: {e}")

