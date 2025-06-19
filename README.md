# 🎹 Piano Roll Generator

A desktop app that turns `.mid` files into animated piano roll videos.  
> [English](#english) | [Français](#francais)

---

## 🔔 Incoming

🔧 **Coming soon:** Support for `.wav` and `.mp3` audio file import!  
This feature will let you visualize standard audio as a piano roll — stay tuned for the next release.

---

## English

### 📝 Description

**Piano Roll App** is a Python desktop application that lets you import `.mid` files and generate synchronized animated piano roll videos with sound.

This repository now contains the full **source code**.  
You can run it with Python, or download a precompiled `.exe` for Windows users.

### 🚀 How to Run (from source)

1. Clone the repo:
   ```
   git clone https://github.com/Akulliaa/Piano-Roll-App.git
   cd Piano-Roll-App
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the app:
   ```
   python main.py
   ```

> 💡 **Don’t want to install Python?**  
> Download and run [`PianoApp.exe`](./public/PianoApp.exe)

---

### 📁 Project Structure

- `main.py` — App entry point  
- `public/imports/` — Folder for processed MIDI data  
- `Tutorial.pdf` — Step-by-step user guide  
- `requirements.txt` — Required Python packages

---

### 🧰 Tech Stack

- **GUI**: PyQt5  
- **MIDI Handling**: `pygame.midi`  
- **Graphics**: QPainter  
- **Logic**: Python standard libraries

---

### 📩 Author

**Lou Fugier**  
📧 [fugierlou@gmail.com](mailto:fugierlou@gmail.com)  
🔗 [LinkedIn](https://www.linkedin.com/in/lou-fugier-828b8a268/)

---

## Francais

### 📝 Description

**Piano Roll App** est une application Python permettant de transformer des fichiers `.mid` en animations synchronisées de type piano roll.

Ce dépôt contient désormais le **code source complet**.  
Vous pouvez l’exécuter avec Python ou télécharger l’exécutable Windows si vous préférez.

### 🚀 Exécuter depuis le code source

1. Cloner le dépôt :
   ```
   git clone https://github.com/Akulliaa/Piano-Roll-App.git
   cd Piano-Roll-App
   ```

2. Installer les dépendances :
   ```
   pip install -r requirements.txt
   ```

3. Lancer l’application :
   ```
   python main.py
   ```

> 💡 **Pas envie d’installer Python ?**  
> Téléchargez et exécutez [`PianoApp.exe`](./public/PianoApp.exe)

---

### 📁 Structure du projet

- `main.py` — Fichier principal  
- `public/imports/` — Dossier contenant les fichiers MIDI traités  
- `Tutorial.pdf` — Guide d’utilisation pas à pas  
- `requirements.txt` — Dépendances Python

---

### 🧰 Technologies utilisées

- **Interface graphique** : PyQt5  
- **Gestion MIDI** : `pygame.midi`  
- **Affichage graphique** : QPainter  
- **Logique** : Bibliothèques standards Python

---

### 📩 Auteur

**Lou Fugier**  
📧 [fugierlou@gmail.com](mailto:fugierlou@gmail.com)  
🔗 [LinkedIn](https://www.linkedin.com/in/lou-fugier-828b8a268/)
