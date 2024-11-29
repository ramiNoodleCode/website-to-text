import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque
import time
import argparse
import logging
import os
from crawler_utils import (create_session_with_retries, normalize_url, setup_directories_and_logging,
                           get_output_filename, CRAWLER_DATA_DIR, LOGS_DIR)

def crawl_website(start_url):
    setup_directories_and_logging(os.path.join(LOGS_DIR, 'crawler.log'))
    output_filename = get_output_filename(start_url)
    
    # Initialize variables
    queue = deque([start_url])
    visited = set()
    session = create_session_with_retries()
    parsed_start_url = urlparse(start_url)
    domain = parsed_start_url.netloc
    start_path = parsed_start_url.path
    
    with open(output_filename, 'w', encoding='utf-8') as output_file:
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

                # Extract and save the text content
                text_content = soup.get_text(separator='\n', strip=True)
                output_file.write(f"Content from {norm_url}:\n\n")
                output_file.write(text_content)
                output_file.write("\n\n" + "="*80 + "\n\n")

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
    print(f"Crawled content saved to: {output_filename}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Crawl a website and save its text content.')
    parser.add_argument('start_url', help='The starting URL of the website to crawl.')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    start_url = args.start_url
    crawl_website(start_url)