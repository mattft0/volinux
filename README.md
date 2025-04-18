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

- Frontend : React.js avec Tailwind CSS
- Backend : FastAPI (Python)
- Base de données : PostgreSQL
- Cache : Redis
- Stockage : MinIO/S3
- Containerisation : Docker

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
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

3. Lancer les services
```bash
docker-compose up -d
```

4. Accéder à l'application
- Frontend : http://localhost:3000
- Backend : http://localhost:8000
- API Docs : http://localhost:8000/docs

## Structure du Projet

```
volinux/
├── frontend/          # Application React
├── backend/           # API FastAPI
├── worker/            # Tâches d'analyse
├── profiles/          # Profils validés
├── uploads/           # Dumps temporaires
├── reports/           # Rapports générés
└── docker/            # Configuration Docker
```

## Licence

MIT License - Voir le fichier LICENSE pour plus de détails.