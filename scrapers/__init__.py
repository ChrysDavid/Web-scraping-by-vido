"""
Module de scraping web et téléchargement YouTube
Contient les classes WebScraper et YoutubeDownloader
"""

from .web_scraper import WebScraper
from .youtube_scraper import YoutubeDownloader
from .utils import (
    sanitize_filename, 
    is_allowed_domain, 
    get_file_extension,
    validate_url,
    is_youtube_url,
    format_file_size,
    cleanup_old_downloads
)

__all__ = [
    'WebScraper',
    'YoutubeDownloader', 
    'sanitize_filename',
    'is_allowed_domain',
    'get_file_extension',
    'validate_url',
    'is_youtube_url',
    'format_file_size',
    'cleanup_old_downloads'
]