from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
import threading
import time
from datetime import datetime
import json
import logging
from scrapers.web_scraper import WebScraper
from scrapers.youtube_scraper import YoutubeDownloader
from scrapers.utils import get_download_status, cleanup_old_downloads
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Configuration des logs
logging.basicConfig(
    filename='logs/scraper.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)

# Dictionnaire pour suivre l'état des tâches
task_status = {}

@app.route('/')
def index():
    """Page d'accueil avec les options de scraping"""
    return render_template('index.html')

@app.route('/web-scraping')
def web_scraping():
    """Interface pour le web scraping"""
    return render_template('web_scraping.html')

@app.route('/youtube-download')
def youtube_download():
    """Interface pour le téléchargement YouTube"""
    return render_template('youtube.html')

@app.route('/start-web-scraping', methods=['POST'])
def start_web_scraping():
    """Lance le scraping web en arrière-plan"""
    try:
        data = request.get_json()
        url = data.get('url')
        options = data.get('options', {})
        
        if not url:
            return jsonify({'error': 'URL manquante'}), 400
        
        # Génération d'un ID unique pour la tâche
        task_id = f"web_{int(time.time())}"
        
        # Configuration du scraper
        output_folder = os.path.join('downloads', 'web_content', task_id)
        
        # Lancement en arrière-plan
        thread = threading.Thread(
            target=run_web_scraping,
            args=(task_id, url, output_folder, options)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'task_id': task_id,
            'message': 'Scraping démarré',
            'status': 'running'
        })
        
    except Exception as e:
        logging.error(f"Erreur lors du démarrage du web scraping: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/start-youtube-download', methods=['POST'])
def start_youtube_download():
    """Lance le téléchargement YouTube en arrière-plan"""
    try:
        data = request.get_json()
        url = data.get('url')
        options = data.get('options', {})
        
        if not url:
            return jsonify({'error': 'URL manquante'}), 400
        
        # Génération d'un ID unique pour la tâche
        task_id = f"youtube_{int(time.time())}"
        
        # Configuration du téléchargeur
        output_folder = os.path.join('downloads', 'youtube_content', task_id)
        
        # Lancement en arrière-plan
        thread = threading.Thread(
            target=run_youtube_download,
            args=(task_id, url, output_folder, options)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'task_id': task_id,
            'message': 'Téléchargement démarré',
            'status': 'running'
        })
        
    except Exception as e:
        logging.error(f"Erreur lors du démarrage du téléchargement YouTube: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/task-status/<task_id>')
def get_task_status(task_id):
    """Récupère l'état d'une tâche"""
    status = task_status.get(task_id, {'status': 'not_found'})
    return jsonify(status)

@app.route('/download/<task_id>')
def download_result(task_id):
    """Télécharge le résultat d'une tâche"""
    try:
        # Trouver le dossier de téléchargement
        web_folder = os.path.join('downloads', 'web_content', task_id)
        youtube_folder = os.path.join('downloads', 'youtube_content', task_id)
        
        if os.path.exists(web_folder):
            # Créer un ZIP du contenu web
            import zipfile
            zip_path = f"{web_folder}.zip"
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for root, dirs, files in os.walk(web_folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, web_folder)
                        zipf.write(file_path, arcname)
            
            return send_file(zip_path, as_attachment=True, download_name=f"web_content_{task_id}.zip")
        
        elif os.path.exists(youtube_folder):
            # Pour YouTube, renvoyer le premier fichier trouvé
            for file in os.listdir(youtube_folder):
                file_path = os.path.join(youtube_folder, file)
                if os.path.isfile(file_path):
                    return send_file(file_path, as_attachment=True)
        
        return jsonify({'error': 'Fichier non trouvé'}), 404
        
    except Exception as e:
        logging.error(f"Erreur lors du téléchargement: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/results')
def results():
    """Page des résultats avec historique"""
    # Récupérer l'historique des tâches
    history = []
    for task_id, status in task_status.items():
        if status.get('status') == 'completed':
            history.append({
                'task_id': task_id,
                'type': 'Web Scraping' if task_id.startswith('web_') else 'YouTube',
                'url': status.get('url', ''),
                'completed_at': status.get('completed_at', ''),
                'files_count': status.get('files_count', 0)
            })
    
    return render_template('results.html', history=history)

def run_web_scraping(task_id, url, output_folder, options):
    """Exécute le web scraping"""
    try:
        task_status[task_id] = {
            'status': 'running',
            'url': url,
            'started_at': datetime.now().isoformat(),
            'progress': 0
        }
        
        scraper = WebScraper(output_folder)
        
        # Configuration des options
        scraper.max_pages = options.get('max_pages', 10)
        scraper.download_images = options.get('download_images', True)
        scraper.download_css = options.get('download_css', True)
        scraper.download_js = options.get('download_js', True)
        scraper.follow_external_links = options.get('follow_external_links', False)
        
        # Callback pour suivre le progrès
        def progress_callback(current, total):
            task_status[task_id]['progress'] = int((current / total) * 100)
        
        scraper.set_progress_callback(progress_callback)
        
        # Lancement du scraping
        scraper.start_scraping(url)
        
        # Finalisation
        files_count = scraper.get_files_count()
        task_status[task_id].update({
            'status': 'completed',
            'completed_at': datetime.now().isoformat(),
            'files_count': files_count,
            'progress': 100
        })
        
        scraper.close()
        logging.info(f"Web scraping terminé pour {task_id}: {files_count} fichiers")
        
    except Exception as e:
        task_status[task_id] = {
            'status': 'error',
            'error': str(e),
            'completed_at': datetime.now().isoformat()
        }
        logging.error(f"Erreur lors du web scraping {task_id}: {e}")

def run_youtube_download(task_id, url, output_folder, options):
    """Exécute le téléchargement YouTube"""
    try:
        task_status[task_id] = {
            'status': 'running',
            'url': url,
            'started_at': datetime.now().isoformat(),
            'progress': 0
        }
        
        downloader = YoutubeDownloader(output_folder)
        
        # Configuration des options
        quality = options.get('quality', 'best')
        audio_only = options.get('audio_only', False)
        is_playlist = options.get('is_playlist', False)
        
        # Callback pour suivre le progrès
        def progress_callback(progress_info):
            if 'percentage' in progress_info:
                percentage = progress_info['percentage']
                if percentage:
                    task_status[task_id]['progress'] = int(percentage)
        
        downloader.set_progress_callback(progress_callback)
        
        # Lancement du téléchargement
        if is_playlist:
            result = downloader.download_playlist(url, quality, audio_only)
        else:
            result = downloader.download_video(url, quality, audio_only)
        
        # Finalisation
        task_status[task_id].update({
            'status': 'completed',
            'completed_at': datetime.now().isoformat(),
            'files_count': result.get('files_count', 1),
            'progress': 100
        })
        
        logging.info(f"Téléchargement YouTube terminé pour {task_id}")
        
    except Exception as e:
        task_status[task_id] = {
            'status': 'error',
            'error': str(e),
            'completed_at': datetime.now().isoformat()
        }
        logging.error(f"Erreur lors du téléchargement YouTube {task_id}: {e}")

# Nettoyage périodique des anciens téléchargements
@app.before_request
def setup_cleanup():
    """Configure le nettoyage automatique"""
    def cleanup_task():
        while True:
            time.sleep(3600)  # Toutes les heures
            cleanup_old_downloads('downloads', max_age_hours=24)
    
    cleanup_thread = threading.Thread(target=cleanup_task)
    cleanup_thread.daemon = True
    cleanup_thread.start()

if __name__ == '__main__':
    # Créer les dossiers nécessaires
    os.makedirs('downloads/web_content', exist_ok=True)
    os.makedirs('downloads/youtube_content', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)