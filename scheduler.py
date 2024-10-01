import os
import sys
import time
import logging
import schedule
from channels import ChannelOperations
from dotenv import load_dotenv

# Enhanced logging configuration
logging.basicConfig(
    filename='scheduler.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Scheduler:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.load_env()
        self.operation = ChannelOperations(os.getenv('YOUTUBE_API_KEY'))
        self.user = os.getenv('USER_NAME')
        logging.info(f"Scheduler initialized. Script directory: {self.script_dir}")

    def load_env(self):
        dotenv_path = os.path.join(self.script_dir, '.env')
        load_dotenv(dotenv_path)
        logging.info(f"Environment variables loaded from {dotenv_path}")

    def setup_jobs(self):
        # Schedule jobs
        schedule.every(69).hours.do(self.run, task='update_sub_channel_videos')
        schedule.every(23).hours.do(self.run, task='generate_playlist_for_tomorrow')
        
        logging.info("Jobs scheduled successfully")

    def run(self, task):
        logging.info(f"Starting run method with task: {task}")
        logging.info(f"Current working directory: {os.getcwd()}")
        logging.info(f"Content of current directory: {os.listdir('.')}")
        self.load_env()  # Reload environment variables
        logging.info(f"Environment variables after reload: {os.environ}")
        
        if task == 'update_sub_channel_videos':
            self._run_task(self.operation.save_videos, self.user, description="updating sub-channel videos")
        elif task == 'generate_playlist_for_tomorrow':
            self._run_task(self.operation.update_playlist, self.user, description="generating playlist for tomorrow")
        else:
            logging.warning(f"Unknown task: {task}")

    def _run_task(self, task_func, *args, description):
        try:
            task_func(*args)
            logging.info(f"Successfully completed task: {description}")
        except Exception as e:
            logging.error(f"Error {description}: {str(e)}", exc_info=True)

    def start(self):
        self.setup_jobs()
        logging.info("Starting scheduler")
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    scheduler = Scheduler()
    scheduler.start()