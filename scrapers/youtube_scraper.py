from yt_dlp import YoutubeDL
import os
import logging
from .utils import sanitize_filename

class YoutubeDownloader:
    def __init__(self, output_folder):
        self.output_folder = output_folder
        self.progress_callback = None
        self.files_count = 0
        
        # Configuration du logging
        self.logger = logging.getLogger(__name__)
        
        # Créer le dossier de sortie
        os.makedirs(output_folder, exist_ok=True)

    def set_progress_callback(self, callback):
        """Définit le callback pour suivre le progrès"""
        self.progress_callback = callback

    def progress_hook(self, d):
        """Hook de progrès pour yt-dlp"""
        if self.progress_callback:
            if d['status'] == 'downloading':
                # Extraire le pourcentage depuis la chaîne
                percent_str = d.get('_percent_str', '0%')
                try:
                    percentage = float(percent_str.replace('%', '').strip())
                    self.progress_callback({'percentage': percentage})
                except (ValueError, AttributeError):
                    pass
            elif d['status'] == 'finished':
                self.progress_callback({'percentage': 100})
                self.files_count += 1

    def get_video_info(self, url):
        """Récupère les informations d'une vidéo sans la télécharger"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title', 'Titre non disponible'),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'uploader': info.get('uploader', 'Auteur non disponible'),
                    'upload_date': info.get('upload_date', 'Date non disponible'),
                    'description': info.get('description', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'formats': [f for f in info.get('formats', []) if f.get('vcodec') != 'none']
                }
        except Exception as e:
            self.logger.error(f"Erreur lors de l'extraction des infos de {url}: {e}")
            return None

    def download_video(self, url, quality='best', audio_only=False):
        """Télécharge une vidéo unique"""
        try:
            # Configuration de base
            if audio_only:
                format_selector = 'bestaudio/best'
                outtmpl = os.path.join(self.output_folder, '%(title)s.%(ext)s')
            else:
                if quality == 'best':
                    format_selector = 'best'
                elif quality == 'worst':
                    format_selector = 'worst'
                else:
                    format_selector = f'best[height<={quality}]'
                outtmpl = os.path.join(self.output_folder, '%(title)s.%(ext)s')

            ydl_opts = {
                'format': format_selector,
                'outtmpl': outtmpl,
                'progress_hooks': [self.progress_hook],
                'extractaudio': audio_only,
                'audioformat': 'mp3' if audio_only else None,
                'ignoreerrors': True,
            }

            with YoutubeDL(ydl_opts) as ydl:
                # Récupérer les infos avant téléchargement
                info = ydl.extract_info(url, download=False)
                if not info:
                    raise Exception("Impossible de récupérer les informations de la vidéo")

                # Télécharger
                ydl.download([url])
                
                return {
                    'success': True,
                    'title': info.get('title', 'Titre inconnu'),
                    'files_count': 1,
                    'message': 'Téléchargement terminé avec succès'
                }

        except Exception as e:
            self.logger.error(f"Erreur lors du téléchargement de {url}: {e}")
            return {
                'success': False,
                'error': str(e),
                'files_count': 0
            }

    def download_playlist(self, url, quality='best', audio_only=False):
        """Télécharge une playlist complète"""
        try:
            # Configuration pour playlist
            if audio_only:
                format_selector = 'bestaudio/best'
                outtmpl = os.path.join(self.output_folder, '%(playlist_title)s', '%(title)s.%(ext)s')
            else:
                if quality == 'best':
                    format_selector = 'best'
                elif quality == 'worst':
                    format_selector = 'worst'
                else:
                    format_selector = f'best[height<={quality}]'
                outtmpl = os.path.join(self.output_folder, '%(playlist_title)s', '%(title)s.%(ext)s')

            ydl_opts = {
                'format': format_selector,
                'outtmpl': outtmpl,
                'progress_hooks': [self.progress_hook],
                'extractaudio': audio_only,
                'audioformat': 'mp3' if audio_only else None,
                'noplaylist': False,
                'ignoreerrors': True,
            }

            with YoutubeDL(ydl_opts) as ydl:
                # Récupérer les infos de la playlist
                info = ydl.extract_info(url, download=False)
                if not info:
                    raise Exception("Impossible de récupérer les informations de la playlist")

                playlist_count = len(info.get('entries', []))
                
                # Télécharger la playlist
                ydl.download([url])
                
                return {
                    'success': True,
                    'playlist_title': info.get('title', 'Playlist'),
                    'files_count': playlist_count,
                    'message': f'Téléchargement de {playlist_count} vidéos terminé'
                }

        except Exception as e:
            self.logger.error(f"Erreur lors du téléchargement de la playlist {url}: {e}")
            return {
                'success': False,
                'error': str(e),
                'files_count': 0
            }

    def download_audio_only(self, url, is_playlist=False):
        """Télécharge uniquement l'audio (alias pour audio_only=True)"""
        if is_playlist:
            return self.download_playlist(url, audio_only=True)
        else:
            return self.download_video(url, audio_only=True)

    def get_available_formats(self, url):
        """Récupère les formats disponibles pour une vidéo"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'listformats': True,
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                formats = info.get('formats', [])
                
                # Filtrer et organiser les formats
                video_formats = []
                audio_formats = []
                
                for f in formats:
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                        # Format vidéo+audio
                        video_formats.append({
                            'format_id': f.get('format_id'),
                            'ext': f.get('ext'),
                            'resolution': f.get('resolution', f'{f.get("width", "?")}x{f.get("height", "?")}'),
                            'fps': f.get('fps'),
                            'vcodec': f.get('vcodec'),
                            'acodec': f.get('acodec'),
                            'filesize': f.get('filesize'),
                        })
                    elif f.get('acodec') != 'none' and f.get('vcodec') == 'none':
                        # Format audio seulement
                        audio_formats.append({
                            'format_id': f.get('format_id'),
                            'ext': f.get('ext'),
                            'acodec': f.get('acodec'),
                            'abr': f.get('abr'),
                            'filesize': f.get('filesize'),
                        })
                
                return {
                    'video_formats': video_formats,
                    'audio_formats': audio_formats
                }
                
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des formats pour {url}: {e}")
            return {'video_formats': [], 'audio_formats': []}

    def cleanup(self):
        """Nettoie les fichiers temporaires"""
        try:
            # Supprimer les fichiers .part (téléchargements interrompus)
            for root, dirs, files in os.walk(self.output_folder):
                for file in files:
                    if file.endswith('.part'):
                        file_path = os.path.join(root, file)
                        os.remove(file_path)
                        self.logger.info(f"Fichier temporaire supprimé: {file_path}")
        except Exception as e:
            self.logger.error(f"Erreur lors du nettoyage: {e}")

    def get_files_count(self):
        """Retourne le nombre de fichiers téléchargés"""
        return self.files_count