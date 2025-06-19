# Système de Recommandation - Backend Django REST API

Ce projet universitaire consiste en un système de recommandation hybride qui combine le filtrage collaboratif et le filtrage basé sur le contenu pour fournir des recommandations personnalisées de livres et de films.

## 🚀 Fonctionnalités

- **Authentification JWT** sécurisée
- **Système de recommandation hybride** combinant :
  - Filtrage collaboratif (User-based, Item-based, SVD)
  - Filtrage basé sur le contenu
  - Approche hybride pondérée
- **API RESTful** documentée avec Swagger/ReDoc
- **Gestion des utilisateurs** avec profils personnalisés
- **Support multi-contenu** (livres et films)

## 🛠 Architecture Technique

### Backend (Django REST Framework)

#### Modèles de données
- `CustomUser`: Utilisateur personnalisé avec préférences
- `Item`: Contenu recommandable (livres, films)
- `Interaction`: Interactions utilisateur-contenu

#### Algorithmes de recommandation
1. **Filtrage Collaboratif**
   - Implémentation de SVD (Singular Value Decomposition)
   - Similarité utilisateur-utilisateur
   - Similarité item-item

2. **Filtrage Basé sur le Contenu**
   - Vectorisation TF-IDF des descriptions
   - Similarité cosinus

3. **Système Hybride**
   - Combinaison pondérée des approches
   - Optimisation des recommandations

## 🔧 Installation

1. Cloner le repository :
```bash
git clone [URL_DU_REPO]
cd recommandation_system_G6
```

2. Créer et activer un environnement virtuel :
```bash
python -m venv myEnv
myEnv\Scripts\activate  # Windows
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Configurer la base de données :
```bash
cd backend
python manage.py migrate
```

5. Lancer le serveur :
```bash
python manage.py runserver
```

## 📚 Documentation API

La documentation de l'API est disponible aux endpoints suivants :
- Swagger UI : `/api/swagger/`
- ReDoc : `/api/redoc/`

### Endpoints principaux

- **Authentification**
  - `POST /api/register/` : Inscription
  - `POST /api/login/` : Connexion
  - `POST /api/token/refresh/` : Rafraîchir le token

- **Profil**
  - `GET /api/profile/` : Obtenir le profil utilisateur

- **Recommandations**
  - `GET /api/recommend/user/` : Recommandations personnalisées
  - `GET /api/recommend/item/` : Recommandations similaires

## 🔐 Sécurité

- Authentification JWT avec tokens d'accès et de rafraîchissement
- Durée de vie configurable des tokens
- Blacklist des tokens révoqués

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push sur la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📧 Contact

Developer Mossoko - camara13fs@gmail.com