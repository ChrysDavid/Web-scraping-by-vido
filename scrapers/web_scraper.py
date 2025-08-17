from selenium import webdriver 
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import os
import time
import requests
import re
import hashlib
import urllib3
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import ssl
import certifi
import logging
from .utils import is_allowed_domain, sanitize_filename, get_file_extension

class WebScraper:
    def __init__(self, output_folder):
        self.output_folder = output_folder
        self.css_folder = os.path.join(output_folder, "css")
        self.js_folder = os.path.join(output_folder, "js")
        self.images_folder = os.path.join(output_folder, "images")
        self.fonts_folder = os.path.join(output_folder, "fonts")
        self.visited_urls = set()
        self.base_domain = ""
        self.files_count = 0
        self.total_size = 0
        self.progress_callback = None
        self.current_page = 0
        self.total_pages_estimate = 1
        
        # Options configurables
        self.max_pages = 10
        self.download_images = True
        self.download_css = True
        self.download_js = True
        self.download_fonts = True
        self.follow_external_links = False
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.max_total_size = 100 * 1024 * 1024  # 100MB
        self.delay = 1  # Délai entre les requêtes
        
        self.create_folders()
        self.session = self.create_session()
        self.setup_driver()
        
        # Configuration du logging
        self.logger = logging.getLogger(__name__)

    def create_session(self):
        """Crée une session requests configurée avec retry et SSL"""
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        session.verify = certifi.where()
        
        # Headers par défaut
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        return session

    def setup_driver(self):
        """Configure le driver Chrome"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--ignore-ssl-errors")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            from chromedriver_py import binary_path
            service = Service(binary_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except ImportError:
            # Fallback si chromedriver_py n'est pas disponible
            self.driver = webdriver.Chrome(options=chrome_options)
        
        self.driver.set_page_load_timeout(30)

    def create_folders(self):
        """Crée les dossiers nécessaires pour organiser les fichiers"""
        folders = [
            self.output_folder, 
            self.css_folder, 
            self.js_folder, 
            self.images_folder,
            self.fonts_folder
        ]
        for folder in folders:
            os.makedirs(folder, exist_ok=True)

    def set_progress_callback(self, callback):
        """Définit le callback pour suivre le progrès"""
        self.progress_callback = callback

    def update_progress(self):
        """Met à jour le progrès"""
        if self.progress_callback and self.total_pages_estimate > 0:
            progress = min((self.current_page / self.total_pages_estimate) * 100, 100)
            self.progress_callback(self.current_page, self.total_pages_estimate)

    def generate_filename(self, content, extension):
        """Génère un nom de fichier unique basé sur le contenu"""
        if isinstance(content, str):
            content = content.encode()
        hash_object = hashlib.md5(content)
        return f"{hash_object.hexdigest()[:8]}{extension}"

    def check_file_constraints(self, file_size):
        """Vérifie les contraintes de taille de fichier"""
        if file_size > self.max_file_size:
            self.logger.warning(f"Fichier trop volumineux: {file_size} bytes")
            return False
        
        if self.total_size + file_size > self.max_total_size:
            self.logger.warning("Limite de taille totale atteinte")
            return False
        
        return True

    def download_external_file(self, url, folder, file_type="unknown"):
        """Télécharge un fichier externe avec gestion des erreurs améliorée"""
        try:
            # Vérifier si le type de fichier doit être téléchargé
            if file_type == "image" and not self.download_images:
                return None
            elif file_type == "css" and not self.download_css:
                return None
            elif file_type == "js" and not self.download_js:
                return None
            elif file_type == "font" and not self.download_fonts:
                return None
            
            # Requête HEAD pour vérifier la taille
            head_response = self.session.head(url, timeout=10)
            content_length = head_response.headers.get('content-length')
            if content_length and not self.check_file_constraints(int(content_length)):
                return None
            
            response = self.session.get(url, timeout=10, stream=True)
            response.raise_for_status()
            
            # Vérifier la taille réelle
            content_size = len(response.content)
            if not self.check_file_constraints(content_size):
                return None
            
            parsed_url = urlparse(url)
            file_name = os.path.basename(parsed_url.path)
            
            # Génération de nom de fichier si nécessaire
            if not file_name or '.' not in file_name:
                content_type = response.headers.get('content-type', '').lower()
                if 'javascript' in content_type:
                    file_name = self.generate_filename(response.content, '.js')
                elif 'css' in content_type:
                    file_name = self.generate_filename(response.content, '.css')
                elif 'image' in content_type:
                    extension = get_file_extension(content_type)
                    file_name = self.generate_filename(response.content, extension)
                elif 'font' in content_type:
                    extension = get_file_extension(content_type)
                    file_name = self.generate_filename(response.content, extension)
                else:
                    self.logger.warning(f"Type de contenu non supporté pour {url}: {content_type}")
                    return None
            
            file_name = sanitize_filename(file_name)
            local_path = os.path.join(folder, file_name)
            
            if not os.path.exists(local_path):
                with open(local_path, 'wb') as f:
                    f.write(response.content)
                self.files_count += 1
                self.total_size += content_size
                self.logger.info(f"Fichier téléchargé: {local_path}")
            
            return os.path.relpath(local_path, self.output_folder)
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Erreur lors du téléchargement de {url}: {e}")
        except Exception as e:
            self.logger.error(f"Erreur inattendue lors du téléchargement de {url}: {e}")
        return None

    def extract_inline_styles(self, soup):
        """Extrait les styles CSS inline"""
        if not self.download_css:
            return
            
        style_tags = soup.find_all('style')
        for idx, style in enumerate(style_tags):
            if style.string:
                filename = self.generate_filename(style.string, '.css')
                css_path = os.path.join(self.css_folder, filename)
                
                if not os.path.exists(css_path):
                    with open(css_path, 'w', encoding='utf-8') as f:
                        f.write(style.string)
                    self.files_count += 1
                    self.logger.info(f"Style CSS extrait: {css_path}")
                
                new_link = soup.new_tag('link', rel='stylesheet', href=f'css/{filename}')
                style.replace_with(new_link)

    def extract_inline_scripts(self, soup):
        """Extrait les scripts JS inline"""
        if not self.download_js:
            return
            
        script_tags = soup.find_all('script', string=True)
        for idx, script in enumerate(script_tags):
            if script.string and not script.get('src'):
                filename = self.generate_filename(script.string, '.js')
                js_path = os.path.join(self.js_folder, filename)
                
                if not os.path.exists(js_path):
                    with open(js_path, 'w', encoding='utf-8') as f:
                        f.write(script.string)
                    self.files_count += 1
                    self.logger.info(f"Script JS extrait: {js_path}")
                
                new_script = soup.new_tag('script', src=f'js/{filename}')
                script.replace_with(new_script)

    def process_external_resources(self, soup, base_url):
        """Traite les ressources externes"""
        # CSS
        for link in soup.find_all('link', href=True):
            if link['href'].endswith('.css') or link.get('rel') == ['stylesheet']:
                css_url = urljoin(base_url, link['href'])
                local_path = self.download_external_file(css_url, self.css_folder, "css")
                if local_path:
                    link['href'] = local_path

        # JavaScript
        for script in soup.find_all('script', src=True):
            js_url = urljoin(base_url, script['src'])
            local_path = self.download_external_file(js_url, self.js_folder, "js")
            if local_path:
                script['src'] = local_path

        # Images
        for img in soup.find_all(['img', 'source'], src=True):
            img_url = urljoin(base_url, img['src'])
            local_path = self.download_external_file(img_url, self.images_folder, "image")
            if local_path:
                img['src'] = local_path

        # Fonts (CSS @font-face)
        for link in soup.find_all('link', href=True):
            if any(font_ext in link['href'] for font_ext in ['.woff', '.woff2', '.ttf', '.otf', '.eot']):
                font_url = urljoin(base_url, link['href'])
                local_path = self.download_external_file(font_url, self.fonts_folder, "font")
                if local_path:
                    link['href'] = local_path

    def scrape_page(self, url):
        """Scrape une page et enregistre son contenu"""
        try:
            if url in self.visited_urls or self.current_page >= self.max_pages:
                return

            if len(self.visited_urls) == 0:
                self.base_domain = urlparse(url).netloc

            self.logger.info(f"Démarrage du scraping de {url}...")
            self.visited_urls.add(url)
            self.current_page += 1
            self.update_progress()

            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Attendre que les ressources se chargent
            time.sleep(2)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            self.logger.info("Extraction des styles inline...")
            self.extract_inline_styles(soup)
            
            self.logger.info("Extraction des scripts inline...")
            self.extract_inline_scripts(soup)
            
            self.logger.info("Traitement des ressources externes...")
            self.process_external_resources(soup, url)
            
            # Sauvegarde de la page HTML
            parsed_url = urlparse(url)
            page_name = "index.html" if parsed_url.path == "/" else parsed_url.path.strip("/").replace("/", "_") + ".html"
            page_name = sanitize_filename(page_name)
            html_path = os.path.join(self.output_folder, page_name)
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(soup.prettify())
            
            self.files_count += 1
            self.logger.info(f"Page {url} sauvegardée avec succès!")
            
            # Délai entre les requêtes
            if self.delay > 0:
                time.sleep(self.delay)
            
            # Suivre les liens internes si configuré
            if self.current_page < self.max_pages:
                links = soup.find_all('a', href=True)
                for link in links:
                    next_url = urljoin(url, link['href'])
                    if self.is_internal_link(next_url) and next_url not in self.visited_urls:
                        self.scrape_page(next_url)
            
        except Exception as e:
            self.logger.error(f"Erreur lors du scraping de {url}: {e}")

    def is_internal_link(self, url):
        """Vérifie si le lien est interne au domaine principal"""
        if self.follow_external_links:
            return is_allowed_domain(url)
        
        parsed_url = urlparse(url)
        return parsed_url.netloc == self.base_domain

    def start_scraping(self, start_url):
        """Lance le scraping à partir de l'URL de départ"""
        self.base_domain = urlparse(start_url).netloc
        self.total_pages_estimate = self.max_pages
        self.scrape_page(start_url)

    def get_files_count(self):
        """Retourne le nombre de fichiers téléchargés"""
        return self.files_count

    def get_total_size(self):
        """Retourne la taille totale des fichiers téléchargés"""
        return self.total_size

    def close(self):
        """Ferme le navigateur et nettoie les ressources"""
        if hasattr(self, 'driver'):
            self.driver.quit()
        if hasattr(self, 'session'):
            self.session.close()