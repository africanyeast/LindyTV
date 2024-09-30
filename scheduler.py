import os
import subprocess
import logging
from channels import ChannelOperations
from dotenv import load_dotenv

# logging configuration
logging.basicConfig(
    filename='scheduler.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Scheduler:
    def __init__(self):
        load_dotenv()
        self.operation = ChannelOperations(os.getenv('YOUTUBE_API_KEY'))
        # temporarily gets the username for scheduling from the .env file
        self.user = os.getenv('USER_NAME')
        self.script_dir = os.path.dirname(os.path.abspath(__file__))

    def setup_cron_jobs(self):
        script_path = os.path.join(self.script_dir, 'scheduler.py')
        
        update_video_command = f"python \"{script_path}\" update_sub_channel_videos"
        generate_playlist_command = f"python \"{script_path}\" generate_playlist_for_tomorrow"

        # set up cron jobs
        try:
            # every 72 hours
            subprocess.call(f"(crontab -l; echo '0 */69 * * * {update_video_command}') | crontab -", shell=True)
            logging.info("Cron job set up for updating videos every 69 hours.")
            
            # one hour before midnight (23:00)
            subprocess.call(f"(crontab -l; echo '0 21 * * * {generate_playlist_command}') | crontab -", shell=True)
            logging.info("Cron job set up for generating playlist daily at 9 PM.")
        except Exception as e:
            logging.error(f"Error setting up cron jobs: {e}")

    def run(self, task):
        if task == 'update_sub_channel_videos':
            try:
                self.operation.save_videos(self.user)
                logging.info("Successfully updated sub-channel videos.")
            except Exception as e:
                logging.error(f"Error updating sub-channel videos: {e}")
        elif task == 'generate_playlist_for_tomorrow':
            try:
                self.operation.update_playlist(self.user)
                logging.info("Successfully generated playlist for tomorrow.")
            except Exception as e:
                logging.error(f"Error generating playlist for tomorrow: {e}")
        else:
            logging.warning(f"Unknown task: {task}")

if __name__ == "__main__":
    scheduler = Scheduler()
    scheduler.setup_cron_jobs()
