import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
from collections import deque
import time
import argparse
import logging
import re
import os  # Add this import
from crawler_utils import (create_session_with_retries, normalize_url, setup_directories_and_logging,
                           get_output_filename, CRAWLER_DATA_DIR, LOGS_DIR)

def is_youtube_embed(src):
    """Check if the src attribute is a YouTube embed."""
    youtube_patterns = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/[\w-]+',
        r'(?:https?:\/\/)?(?:www\.)?youtube-nocookie\.com\/embed\/[\w-]+'
    ]
    return any(re.match(pattern, src) for pattern in youtube_patterns)

def get_youtube_video_url(embed_url):
    """Convert YouTube embed URL to standard video URL."""
    parsed_url = urlparse(embed_url)
    video_id = parsed_url.path.split('/')[-1]
    query_params = parse_qs(parsed_url.query)
    
    # Check if there's a 'v' parameter in the query string
    if 'v' in query_params:
        video_id = query_params['v'][0]
    
    return f"https://www.youtube.com/watch?v={video_id}"

def crawl_website(start_url):
    setup_directories_and_logging(os.path.join(LOGS_DIR, 'youtube_crawler.log'))
    youtube_videos_filename = get_output_filename(start_url, '_youtube_videos')
    
    # Initialize variables
    queue = deque([start_url])
    visited = set()
    session = create_session_with_retries()
    parsed_start_url = urlparse(start_url)
    domain = parsed_start_url.netloc
    start_path = parsed_start_url.path
    
    with open(youtube_videos_filename, 'w', encoding='utf-8') as youtube_file:
        while queue:
            url = queue.popleft()
            norm_url = normalize_url(url)

            if norm_url in visited:
                logging.debug(f"Skipping already visited URL: {norm_url}")
                continue
            visited.add(norm_url)

            try:
                logging.info(f"Fetching: {norm_url}")
                print(f"Crawling: {norm_url}")  # Console log
                response = session.get(norm_url, timeout=10)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')

                # Find and log YouTube videos
                youtube_videos = []
                for iframe in soup.find_all('iframe', src=True):
                    src = iframe['src']
                    if is_youtube_embed(src):
                        video_url = get_youtube_video_url(src)
                        youtube_videos.append(video_url)

                if youtube_videos:
                    youtube_file.write(f"YouTube videos found on {norm_url}:\n")
                    for video in youtube_videos:
                        youtube_file.write(f"{video}\n")
                    youtube_file.write("\n")
                    logging.info(f"Found {len(youtube_videos)} YouTube videos on {norm_url}")
                    print(f"Found {len(youtube_videos)} YouTube videos on {norm_url}")

                # Find and process all links on the page
                new_links = 0
                skipped_links = 0
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(norm_url, href)
                    full_url = normalize_url(full_url)
                    parsed_full_url = urlparse(full_url)

                    # Check if the URL is within the same domain and under the specified path
                    if parsed_full_url.netloc != domain:
                        skipped_links += 1
                    elif not parsed_full_url.path.startswith(start_path):
                        skipped_links += 1
                    elif full_url in visited:
                        skipped_links += 1
                    else:
                        queue.append(full_url)
                        new_links += 1
                        logging.debug(f"Added to queue: {full_url}")

                print(f"Found {new_links} new links and skipped {skipped_links} links on {norm_url}")  # Console log

                # Be polite and sleep to avoid overwhelming the server
                time.sleep(1)

            except requests.exceptions.RequestException as e:
                logging.error(f"Error fetching {norm_url}: {e}")
                print(f"Error fetching {norm_url}: {e}")  # Console log

    logging.info(f"Crawl completed. Total pages visited: {len(visited)}")
    print(f"Crawl completed. Total pages visited: {len(visited)}")
    print(f"YouTube videos saved to: {youtube_videos_filename}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Crawl a website and log YouTube videos from all of its pages.')
    parser.add_argument('start_url', help='The starting URL of the website to crawl.')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    start_url = args.start_url
    crawl_website(start_url)