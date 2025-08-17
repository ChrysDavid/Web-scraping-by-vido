# Web Scraper Pro 🚀

Interface web professionnelle pour le scraping de sites web et le téléchargement de contenus YouTube, développée avec Flask.

## ✨ Fonctionnalités

### 🌐 Web Scraping
- Téléchargement complet de sites web (HTML, CSS, JS, images, polices)
- Navigation intelligente entre les pages
- Configuration flexible des options de téléchargement
- Respect des robots.txt et limitations de débit
- Organisation automatique des fichiers

### 📹 YouTube Downloader
- Téléchargement de vidéos individuelles
- Support des playlists complètes
- Choix de la qualité vidéo
- Extraction audio uniquement (MP3)
- Interface intuitive avec aperçu des vidéos

### 🎛️ Interface Web
- Design responsive avec Bootstrap 5
- Suivi en temps réel des téléchargements
- Historique complet des tâches
- Gestion des erreurs avancée
- Interface multilingue (français)

## 🛠️ Installation

### Prérequis
- Python 3.8 ou supérieur
- Google Chrome ou Chromium installé
- Git (pour cloner le projet)

### Installation automatique

```bash
# Cloner le projet
git clone <URL_DU_PROJET>
cd web_scraper_flask

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows:
venv\Scripts\activate
# Sur Linux/Mac:
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python run.py
```

### Installation manuelle

1. **Cloner le projet**
```bash
git clone <URL_DU_PROJET>
cd web_scraper_flask
```

2. **Créer l'environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer l'application**
```bash
# Copier le fichier de configuration
cp config.py.example config.py
# Éditer selon vos besoins
```

5. **Lancer l'application**
```bash
python run.py
```

## 📁 Structure du projet

```
web_scraper_flask/
│
├── app.py                      # Application Flask principale
├── config.py                  # Configuration
├── run.py                     # Script de lancement
├── requirements.txt           # Dépendances Python
├── README.md                  # Documentation
│
├── scrapers/                  # Modules de scraping
│   ├── __init__.py
│   ├── web_scraper.py        # Scraper web avec Selenium
│   ├── youtube_scraper.py    # Téléchargeur YouTube
│   └── utils.py              # Utilitaires communs
│
├── templates/                 # Templates HTML
│   ├── base.html             # Template de base
│   ├── index.html            # Page d'accueil
│   ├── web_scraping.html     # Interface web scraping
│   ├── youtube.html          # Interface YouTube
│   └── results.html          # Historique
│
├── static/                   # Fichiers statiques
│   ├── css/
│   │   └── style.css        # Styles personnalisés
│   └── js/
│       └── main.js          # JavaScript principal
│
├── downloads/                # Dossier des téléchargements
│   ├── web_content/         # Contenu web
│   └── youtube_content/     # Vidéos YouTube
│
└── logs/                    # Fichiers de logs
    └── app.log
```

## 🚀 Utilisation

### Démarrage rapide

1. **Lancer l'application**
```bash
python run.py
```

2. **Ouvrir votre navigateur** et aller sur `http://localhost:5000`

3. **Choisir votre mode** :
   - **Web Scraping** : Pour télécharger des sites web
   - **YouTube** : Pour télécharger des vidéos YouTube

### Web Scraping

1. Entrez l'URL du site à scraper
2. Configurez les options :
   - Nombre maximum de pages
   - Types de fichiers à télécharger
   - Délai entre les requêtes
3. Cliquez sur "Démarrer le Scraping"
4. Suivez la progression en temps réel
5. Téléchargez le fichier ZIP généré

### YouTube Downloader

1. Collez l'URL de la vidéo ou playlist YouTube
2. Choisissez les options :
   - Qualité vidéo
   - Audio seulement (MP3)
   - Type de contenu (vidéo/playlist)
3. Cliquez sur "Télécharger"
4. Récupérez vos fichiers

## ⚙️ Configuration

Éditez le fichier `config.py` pour personnaliser :

```python
class Config:
    # Scraping web
    DEFAULT_MAX_PAGES = 10
    DEFAULT_TIMEOUT = 30
    
    # YouTube
    DEFAULT_QUALITY = 'best'
    
    # Sécurité
    ALLOWED_DOMAINS = []  # Vide = tous autorisés
    BLOCKED_DOMAINS = ['facebook.com', 'instagram.com']
    
    # Limites
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_TOTAL_SIZE = 100 * 1024 * 1024  # 100MB
```

## 🔧 API Endpoints

### Routes principales
- `GET /` - Page d'accueil
- `GET /web-scraping` - Interface web scraping
- `GET /youtube-download` - Interface YouTube
- `GET /results` - Historique des téléchargements

### API REST
- `POST /start-web-scraping` - Démarre un scraping web
- `POST /start-youtube-download` - Démarre un téléchargement YouTube
- `GET /task-status/<task_id>` - Statut d'une tâche
- `GET /download/<task_id>` - Télécharge les résultats

## 🐛 Dépannage

### Problèmes courants

**Chrome/ChromeDriver non trouvé**
```bash
# Installer Chrome sur Ubuntu/Debian
sudo apt update && sudo apt install google-chrome-stable

# Vérifier l'installation
google-chrome --version
```

**Erreur de permissions**
```bash
# Donner les permissions d'exécution
chmod +x run.py
```

**Port déjà utilisé**
```bash
# Utiliser un autre port
export PORT=8080
python run.py
```

### Logs et débogage

Les logs sont disponibles dans :
- `logs/app.log` - Logs généraux
- `logs/scraper.log` - Logs de scraping
- Console du navigateur - Erreurs JavaScript

Pour activer le mode debug :
```bash
export FLASK_DEBUG=true
python run.py
```

## 📋 TODO / Améliorations futures

- [ ] Support de l'authentification utilisateur
- [ ] API REST complète avec documentation Swagger
- [ ] Support de plus de plateformes (Vimeo, etc.)
- [ ] Planification de tâches récurrentes
- [ ] Interface d'administration avancée
- [ ] Support des proxies
- [ ] Optimisations de performance
- [ ] Tests unitaires complets
- [ ] Docker et déploiement en production

## 🤝 Contribution

Les contributions sont les bienvenues ! 

1. Fork le projet
2. Créez une branche pour votre fonctionnalité
3. Committez vos changements
4. Poussez vers la branche
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

Pour obtenir de l'aide :
- Ouvrez une issue sur GitHub
- Consultez la documentation
- Vérifiez les logs d'erreur

## 🔥 Fonctionnalités avancées

### Configuration personnalisée
- Créez un fichier `.env` pour vos variables d'environnement
- Personnalisez les headers HTTP
- Configurez les timeouts et retry

### Surveillance système
- Monitoring de l'usage des ressources
- Alertes en cas d'erreur
- Statistiques détaillées

### Sécurité
- Validation stricte des URLs
- Sandbox pour l'exécution des scrapers
- Rate limiting intégré