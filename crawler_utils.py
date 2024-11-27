import os
import requests
from urllib.parse import urljoin, urlparse, urldefrag
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import re
import logging

# Update the common configurations
CRAWLER_DATA_DIR = os.path.join(os.path.dirname(__file__), 'crawler-data')
LOGS_DIR = os.path.join(os.path.dirname(__file__), 'logs')

def create_session_with_retries():
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

def normalize_url(url):
    """Normalize URL by removing fragments."""
    url, frag = urldefrag(url)
    return url

def get_filename_from_url(url, suffix=''):
    """Generate a filename from the given URL."""
    parsed_url = urlparse(url)
    path = parsed_url.path.strip('/')
    filename = re.sub(r'[^\w\-_\. ]', '_', path)
    return f"{parsed_url.netloc}_{filename}{suffix}.txt"

def setup_directories_and_logging(log_filename):
    # Create directories if they don't exist
    os.makedirs(CRAWLER_DATA_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)

    # Set up logging
    logging.basicConfig(filename=os.path.join(LOGS_DIR, log_filename), level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

def get_output_filename(start_url, suffix=''):
    return os.path.join(CRAWLER_DATA_DIR, get_filename_from_url(start_url, suffix))