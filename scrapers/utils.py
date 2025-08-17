import os
import re
import time
import shutil
from urllib.parse import urlparse
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def sanitize_filename(filename):
    """Assainit un nom de fichier en supprimant les caractères non autorisés"""
    # Remplacer les caractères interdits
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Supprimer les espaces en début/fin
    filename = filename.strip()
    # Limiter la longueur
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:200-len(ext)] + ext
    return filename

def is_allowed_domain(url):
    """Vérifie si le domaine est autorisé pour le scraping"""
    from config import Config
    
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()
    
    # Vérifier les domaines interdits
    for blocked_domain in Config.BLOCKED_DOMAINS:
        if blocked_domain.lower() in domain:
            return False
    
    # Si une liste de domaines autorisés est définie, la vérifier
    if Config.ALLOWED_DOMAINS:
        for allowed_domain in Config.ALLOWED_DOMAINS:
            if allowed_domain.lower() in domain:
                return True
        return False
    
    return True

def get_file_extension(content_type):
    """Détermine l'extension de fichier à partir du content-type"""
    content_type = content_type.lower().split(';')[0].strip()
    
    extension_map = {
        'text/css': '.css',
        'text/javascript': '.js',
        'application/javascript': '.js',
        'image/jpeg': '.jpg',
        'image/jpg': '.jpg',
        'image/png': '.png',
        'image/gif': '.gif',
        'image/webp': '.webp',
        'image/svg+xml': '.svg',
        'image/x-icon': '.ico',
        'font/woff': '.woff',
        'font/woff2': '.woff2',
        'application/font-woff': '.woff',
        'application/font-woff2': '.woff2',
        'font/truetype': '.ttf',
        'font/opentype': '.otf',
        'application/vnd.ms-fontobject': '.eot',
        'text/html': '.html',
        'application/pdf': '.pdf',
        'text/plain': '.txt',
    }
    
    return extension_map.get(content_type, '')

def get_download_status(task_id, downloads_folder):
    """Récupère le statut d'un téléchargement"""
    web_folder = os.path.join(downloads_folder, 'web_content', task_id)
    youtube_folder = os.path.join(downloads_folder, 'youtube_content', task_id)
    
    status = {
        'exists': False,
        'files_count': 0,
        'total_size': 0,
        'folder_path': None
    }
    
    if os.path.exists(web_folder):
        status['exists'] = True
        status['folder_path'] = web_folder
        status['files_count'] = count_files_in_folder(web_folder)
        status['total_size'] = get_folder_size(web_folder)
    elif os.path.exists(youtube_folder):
        status['exists'] = True
        status['folder_path'] = youtube_folder
        status['files_count'] = count_files_in_folder(youtube_folder)
        status['total_size'] = get_folder_size(youtube_folder)
    
    return status

def count_files_in_folder(folder_path):
    """Compte le nombre de fichiers dans un dossier (récursif)"""
    count = 0
    try:
        for root, dirs, files in os.walk(folder_path):
            count += len(files)
    except Exception as e:
        logger.error(f"Erreur lors du comptage des fichiers dans {folder_path}: {e}")
    return count

def get_folder_size(folder_path):
    """Calcule la taille totale d'un dossier en bytes"""
    total_size = 0
    try:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
    except Exception as e:
        logger.error(f"Erreur lors du calcul de la taille de {folder_path}: {e}")
    return total_size

def format_file_size(size_bytes):
    """Formate une taille en bytes en format lisible"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def cleanup_old_downloads(downloads_folder, max_age_hours=24):
    """Nettoie les anciens téléchargements"""
    try:
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        for content_type in ['web_content', 'youtube_content']:
            content_folder = os.path.join(downloads_folder, content_type)
            
            if not os.path.exists(content_folder):
                continue
            
            for task_folder in os.listdir(content_folder):
                task_path = os.path.join(content_folder, task_folder)
                
                if not os.path.isdir(task_path):
                    continue
                
                # Vérifier l'âge du dossier
                folder_mtime = datetime.fromtimestamp(os.path.getmtime(task_path))
                
                if folder_mtime < cutoff_time:
                    try:
                        shutil.rmtree(task_path)
                        logger.info(f"Dossier ancien supprimé: {task_path}")
                    except Exception as e:
                        logger.error(f"Erreur lors de la suppression de {task_path}: {e}")
        
        # Nettoyer aussi les fichiers ZIP
        for file in os.listdir(downloads_folder):
            if file.endswith('.zip'):
                file_path = os.path.join(downloads_folder, file)
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                if file_mtime < cutoff_time:
                    try:
                        os.remove(file_path)
                        logger.info(f"Fichier ZIP ancien supprimé: {file_path}")
                    except Exception as e:
                        logger.error(f"Erreur lors de la suppression de {file_path}: {e}")
                        
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage des téléchargements: {e}")

def validate_url(url):
    """Valide et normalise une URL"""
    if not url:
        return None, "URL vide"
    
    # Ajouter le schéma si manquant
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return None, "URL invalide"
        
        # Vérifier si le domaine est autorisé
        if not is_allowed_domain(url):
            return None, "Domaine non autorisé"
        
        return url, None
        
    except Exception as e:
        return None, f"Erreur de validation: {str(e)}"

def is_youtube_url(url):
    """Vérifie si l'URL est une URL YouTube"""
    youtube_domains = ['youtube.com', 'youtu.be', 'www.youtube.com', 'm.youtube.com']
    parsed = urlparse(url)
    return parsed.netloc.lower() in youtube_domains

def extract_youtube_id(url):
    """Extrait l'ID d'une vidéo YouTube depuis l'URL"""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]+)',
        r'youtube\.com/embed/([a-zA-Z0-9_-]+)',
        r'youtube\.com/v/([a-zA-Z0-9_-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def create_progress_bar(current, total, bar_length=50):
    """Crée une barre de progression en ASCII"""
    if total == 0:
        return "[" + "=" * bar_length + "] 100%"
    
    progress = min(current / total, 1.0)
    filled_length = int(bar_length * progress)
    bar = "=" * filled_length + "-" * (bar_length - filled_length)
    percentage = int(progress * 100)
    
    return f"[{bar}] {percentage}%"

def log_download_stats(task_id, files_count, total_size, duration):
    """Enregistre les statistiques de téléchargement"""
    stats = {
        'task_id': task_id,
        'files_count': files_count,
        'total_size': format_file_size(total_size),
        'duration': f"{duration:.2f}s",
        'timestamp': datetime.now().isoformat()
    }
    
    logger.info(f"Téléchargement terminé - Stats: {stats}")
    return stats