import os
from datetime import timedelta

class Config:
    """Configuration de l'application Flask"""
    
    # Sécurité
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    
    # Dossiers
    UPLOAD_FOLDER = 'downloads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max pour les uploads
    
    # Web Scraping
    DEFAULT_MAX_PAGES = 10
    DEFAULT_TIMEOUT = 30
    DEFAULT_DELAY = 1
    
    # YouTube
    DEFAULT_QUALITY = 'best'
    ALLOWED_FORMATS = ['mp4', 'webm', 'mp3', 'wav']
    
    # Nettoyage automatique
    AUTO_CLEANUP_ENABLED = True
    MAX_FILE_AGE_HOURS = 24
    CLEANUP_INTERVAL_HOURS = 1
    
    # Headers par défaut pour les requêtes
    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Domaines autorisés pour le scraping (vide = tous autorisés)
    ALLOWED_DOMAINS = []
    
    # Domaines interdits
    BLOCKED_DOMAINS = [
        'facebook.com',
        'instagram.com',
        'twitter.com',
        'linkedin.com'
    ]
    
    # Extensions de fichiers à télécharger
    ALLOWED_EXTENSIONS = {
        'images': {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.ico'},
        'styles': {'.css'},
        'scripts': {'.js'},
        'fonts': {'.woff', '.woff2', '.ttf', '.otf', '.eot'},
        'documents': {'.pdf', '.doc', '.docx', '.txt'}
    }
    
    # Limites de téléchargement
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB par fichier
    MAX_TOTAL_SIZE = 100 * 1024 * 1024  # 100MB par tâche
    
    # Configuration des logs
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s %(message)s'