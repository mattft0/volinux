# Volinux - Analyse de Dumps Mémoire Linux

Volinux est une plateforme web pour l'analyse de dumps mémoire Linux, offrant une interface utilisateur intuitive et des fonctionnalités avancées d'analyse.

## Fonctionnalités

- Interface web conviviale
- Upload sécurisé de dumps mémoire
- Détection automatique du profil
- Validation humaine des profils
- Analyse via plugins Volatility
- Génération de rapports détaillés
- Suppression automatique des dumps après analyse

## Architecture

### Frontend
- React 19.1.0
- Tailwind CSS 3.3.0
- Axios pour les requêtes HTTP
- Testing Library pour les tests
- PostCSS pour le traitement CSS

### Backend
- Flask (Python)
- Flask-CORS pour la gestion CORS
- Volatility pour l'analyse des dumps mémoire
- Logging natif Python pour la gestion des logs

### Outils de Développement
- Node.js 18+ pour le frontend
- Python 3.9+ pour le backend
- Nginx pour le déploiement

## Installation

### Prérequis

- Docker et Docker Compose
- Node.js 18+
- Python 3.9+

### Développement local

1. Cloner le repository
```bash
git clone https://github.com/votre-org/volinux.git
cd volinux
```

2. Installer les dépendances
```bash
# Backend
cd backend-dump-analyzer
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd frontend-dump-analyzer
npm install
```

3. Lancer les services
```bash
# Backend
cd backend-dump-analyzer
uvicorn app:app --reload

# Frontend
cd frontend-dump-analyzer
npm run dev
```

4. Accéder à l'application
- Frontend : http://localhost:3000
- Backend : http://localhost:8000
- API Docs : http://localhost:8000/docs

## Déploiement sur Nginx

### Prérequis

- Serveur Linux avec Nginx installé
- Docker et Docker Compose
- Certbot (pour HTTPS)

### Configuration Nginx

1. Créer un fichier de configuration pour votre site :
```bash
sudo nano /etc/nginx/sites-available/volinux
```

2. Ajouter la configuration suivante :
```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

3. Activer le site :
```bash
sudo ln -s /etc/nginx/sites-available/volinux /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

4. Configurer HTTPS avec Certbot :
```bash
sudo certbot --nginx -d votre-domaine.com
```

### Déploiement de l'application

1. Construire le frontend pour la production :
```bash
cd frontend-dump-analyzer
npm run build
```

2. Configurer le backend pour la production :
```bash
cd backend-dump-analyzer
# Configurer les variables d'environnement
cp .env.example .env
# Modifier les variables selon votre environnement
```

3. Lancer les services :
```bash
# Backend
cd backend-dump-analyzer
gunicorn app:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Frontend (servir les fichiers statiques)
cd frontend-dump-analyzer/build
python -m http.server 3000
```

### Variables d'environnement

Créer un fichier `.env` dans le dossier backend-dump-analyzer avec les variables suivantes :
```env
NODE_ENV=production
API_URL=https://votre-domaine.com/api
```

## Structure du Projet

```
volinux/
├── frontend-dump-analyzer/    # Application React
│   ├── src/                   # Code source React
│   ├── public/                # Fichiers statiques
│   └── package.json           # Dépendances Node.js
└── backend-dump-analyzer/     # API FastAPI
    ├── app.py                 # Application principale
    └── venv/                  # Environnement virtuel Python
```

## Licence

MIT License - Voir le fichier LICENSE pour plus de détails.