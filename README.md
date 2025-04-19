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
flask run

# Frontend
cd frontend-dump-analyzer
npm run dev
```

4. Accéder à l'application
- Frontend : http://localhost:3000
- Backend : http://localhost:5000

## Structure du Projet

```
volinux/
├── frontend-dump-analyzer/    # Application React
│   ├── src/                   # Code source React
│   ├── public/                # Fichiers statiques
│   └── package.json           # Dépendances Node.js
└── backend-dump-analyzer/     # API Flask
    ├── app.py                 # Application principale
    └── venv/                  # Environnement virtuel Python
```

## Licence

MIT License - Voir le fichier LICENSE pour plus de détails.