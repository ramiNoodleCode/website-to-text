# Web Crawler Project

A Python-based web crawling toolkit that includes a general-purpose web crawler and a specialized YouTube video crawler. This project allows you to systematically crawl websites while respecting domain boundaries and collecting either text content or embedded YouTube videos.

## Features

- **General Web Crawler**: Extracts and saves text content from all pages within a specified domain
- **YouTube Video Crawler**: Identifies and saves links to embedded YouTube videos from all pages within a domain
- **Polite Crawling**: Implements delays between requests to avoid overwhelming servers
- **Retry Mechanism**: Handles failed requests with automatic retries
- **Domain Boundary Respect**: Only crawls pages within the specified domain and path
- **Logging**: Comprehensive logging system for debugging and monitoring

## Requirements

```bash
pip install requests
pip install beautifulsoup4
pip install urllib3
```

## Project Structure

- `crawler.py` - General purpose web crawler
- `youtube_video_crawler.py` - Specialized crawler for finding YouTube videos
- `crawler_utils.py` - Shared utilities and configurations
- `crawler-data/` - Directory where crawled content is saved
- `logs/` - Directory for log files

## Usage

### General Web Crawler

```bash
python crawler.py https://example.com [--debug]
```

This will crawl the specified website and save all text content to a file in the `crawler-data` directory.

### YouTube Video Crawler

```bash
python youtube_video_crawler.py https://example.com [--debug]
```

This will crawl the specified website and save all found YouTube video URLs to a file in the `crawler-data` directory.

### Command Line Arguments

- `start_url`: The URL where the crawler should begin (required)
- `--debug`: Enable debug logging (optional)

## Output

### General Crawler
- Creates a text file in `crawler-data/` containing the text content from all crawled pages
- File naming format: `domain_path.txt`

### YouTube Video Crawler
- Creates a text file in `crawler-data/` containing YouTube video URLs
- File naming format: `domain_path_youtube_videos.txt`

## Logging

- Log files are stored in the `logs/` directory
- Two separate log files:
  - `crawler.log` for the general crawler
  - `youtube_crawler.log` for the YouTube video crawler
- Logs include timestamps, log levels, and detailed messages

## Features in Detail

### URL Handling
- Normalizes URLs by removing fragments
- Respects domain boundaries
- Follows relative and absolute links within the same domain
- Stays within the initial path structure

### Error Handling
- Implements retry mechanism for failed requests
- Gracefully handles network errors and timeouts
- Logs all errors for debugging

### Rate Limiting
- Implements a 1-second delay between requests
- Uses session management for efficient connections
- Configurable retry strategy for failed requests

## Best Practices

1. Always check robots.txt before crawling a website
2. Use appropriate delays between requests
3. Handle the crawled data responsibly
4. Respect website terms of service
5. Consider implementing a user agent string

## License

This project is open source and available under the MIT License.