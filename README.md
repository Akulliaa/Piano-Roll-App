# 🎹 Piano Roll Generator

A standalone desktop app that turns `.mid` files into animated piano roll videos.  
>  English | [Français](#-français)

---

## English

### 📝 Description

**Piano Roll App** is a desktop application that allows users to import `.mid` files and generate synchronized animated piano roll videos with sound.  
Designed for Windows, No installation of Python or libraries is required, the app is precompiled.

### 🚀 How to Use

1. Download and run the app: [`PianoApp.exe`](./public/PianoApp.exe)
2. Load your own `.mid` file using the import button.
3. Preview the animation directly.
4. The processed MIDI data is saved in the `/public/imports/` folder.

### 📁 Included Files

- `PianoApp.exe` — The executable app.
- `Tutorial.pdf` — User guide with screenshots.
- `imports/` — Folder used by the app to store transformed MIDI data (do not import from it).

### 🧰 Tech Stack

- **GUI**: PyQt5
- **MIDI Handling**: `pygame.midi`
- **Graphics**: `QPainter `
- **Logic**: Python standard libraries

---

## Français

### 📝 Description

**Piano Roll App** est une application Windows qui permet de transformer des fichiers MIDI (`.mid`) en animations de type piano roll synchronisées avec la musique.  
Fonctionne directement via un exécutable, aucune installation de Python ou de dépendances n’est nécessaire, l’application est déjà compilée..

### 🚀 Utilisation

1. Lancez l’application : [`PianoApp.exe`](./public/PianoApp.exe)
2. Importez votre propre fichier `.mid`.
3. Visualisez l’animation.
4. Les fichiers MIDI transformés sont enregistrés dans le dossier `/public/imports/`.

### 📁 Fichiers fournis

- `PianoApp.exe` — Application autonome.
- `Tutorial.pdf` — Guide d’utilisation avec captures d’écran.
- `imports/` — Dossier utilisé par l’application pour stocker les fichiers MIDI convertis (ne pas utiliser pour l’import).

### 🧰 Technologies

- **GUI**: PyQt5
- **MIDI Handling**: `pygame.midi`
- **Graphics**: `QPainter `
- **Logic**: Python Bibliothèques standards

---

### 📩 Author

**Lou Fugier**  
📧 [fugierlou@gmail.com](mailto:fugierlou@gmail.com)  
🔗 [LinkedIn](https://www.linkedin.com/in/lou-fugier-828b8a268/)
