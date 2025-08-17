#!/usr/bin/env python3
"""
Script de lancement pour Web Scraper Pro
"""

import os
import sys
import logging
from app import app
from config import Config

def create_directories():
    """Crée les dossiers nécessaires s'ils n'existent pas"""
    directories = [
        'downloads',
        'downloads/web_content',
        'downloads/youtube_content', 
        'logs',
        'static/css',
        'static/js',
        'static/img'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Dossier créé/vérifié: {directory}")

def setup_logging():
    """Configure le système de logging"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configuration du logging pour les fichiers
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler('logs/app.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Réduire le niveau de log pour les bibliothèques externes
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('selenium').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    print("✓ Système de logging configuré")

def check_dependencies():
    """Vérifie que toutes les dépendances sont installées"""
    required_modules = [
        'flask',
        'selenium', 
        'beautifulsoup4',
        'requests',
        'yt_dlp',
        'chromedriver_py'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module.replace('-', '_'))
            print(f"✓ {module}")
        except ImportError:
            missing_modules.append(module)
            print(f"✗ {module} - MANQUANT")
    
    if missing_modules:
        print(f"\n❌ Modules manquants: {', '.join(missing_modules)}")
        print("Installez-les avec: pip install -r requirements.txt")
        return False
    
    print("\n✅ Toutes les dépendances sont installées")
    return True

def check_chrome():
    """Vérifie que Chrome/Chromium est disponible"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from chromedriver_py import binary_path
        from selenium.webdriver.chrome.service import Service
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        service = Service(binary_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.quit()
        
        print("✓ Chrome et ChromeDriver sont disponibles")
        return True
        
    except Exception as e:
        print(f"❌ Problème avec Chrome/ChromeDriver: {e}")
        print("Assurez-vous que Chrome est installé sur votre système")
        return False

def print_banner():
    """Affiche la bannière de démarrage"""
    banner = """
    ╔══════════════════════════════════════════════╗
    ║              WEB SCRAPER PRO                 ║
    ║           Interface Flask Complète           ║
    ╚══════════════════════════════════════════════╝
    """
    print(banner)

def print_info():
    """Affiche les informations de l'application"""
    info = f"""
    📋 Informations de l'application:
    ├── Port: {os.environ.get('PORT', 5000)}
    ├── Mode debug: {app.config.get('DEBUG', False)}
    ├── Dossier de téléchargement: downloads/
    ├── Logs: logs/
    └── Configuration: config.py
    
    🌐 URLs disponibles:
    ├── Accueil: http://localhost:5000/
    ├── Web Scraping: http://localhost:5000/web-scraping
    ├── YouTube: http://localhost:5000/youtube-download  
    └── Historique: http://localhost:5000/results
    
    📖 Fonctionnalités:
    ├── ✓ Web scraping avec Selenium
    ├── ✓ Téléchargement YouTube avec yt-dlp
    ├── ✓ Interface web responsive
    ├── ✓ Suivi des tâches en temps réel
    ├── ✓ Historique des téléchargements
    └── ✓ Configuration flexible
    """
    print(info)

def main():
    """Fonction principale"""
    print_banner()
    
    print("🔍 Vérification du système...")
    
    # Créer les dossiers
    create_directories()
    
    # Configurer les logs
    setup_logging()
    
    # Vérifier les dépendances
    if not check_dependencies():
        sys.exit(1)
    
    # Vérifier Chrome
    if not check_chrome():
        print("⚠️  Chrome non détecté, certaines fonctionnalités peuvent ne pas marcher")
        response = input("Continuer quand même ? [y/N]: ")
        if response.lower() != 'y':
            sys.exit(1)
    
    print("\n✅ Système prêt !")
    
    # Afficher les informations
    print_info()
    
    # Configuration du serveur
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Démarrage du serveur sur http://{host}:{port}")
    print("Appuyez sur Ctrl+C pour arrêter le serveur\n")
    
    try:
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 Arrêt du serveur...")
    except Exception as e:
        print(f"❌ Erreur lors du démarrage: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()