import threading
import os
from backend.scheduler import start_collector


def start_scheduler():
    start_collector()


thread = threading.Thread(target=start_scheduler)
thread.daemon = True
thread.start()

os.system("streamlit run dashboard.py")