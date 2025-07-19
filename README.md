# Emanet Subtitle Translator 🎬

Application simple pour traduire automatiquement les dialogues turcs de la série Emanet en sous-titres français de qualité.

## 🎯 Objectif

Permettre à votre grand-mère de profiter pleinement de la série Emanet en comprenant tous les dialogues grâce à des sous-titres français automatiques.

## 🌟 Points forts

- **Traduction de haute qualité** : Utilise NLLB-200 de Meta, un modèle de traduction IA de pointe
- **100% local** : Toute la traduction se fait sur votre ordinateur, pas besoin d'Internet après l'installation
- **Meilleure compréhension** : NLLB comprend mieux le contexte et produit des traductions plus naturelles
- **Respect de la vie privée** : Aucune donnée n'est envoyée sur Internet

## 🚀 Installation rapide

1. **Téléchargez les fichiers** dans un dossier de votre choix

2. **Ouvrez un terminal** dans ce dossier (clic droit → "Ouvrir dans le terminal")

3. **Lancez l'installation** :
   ```bash
   bash install.sh
   ```

4. **C'est prêt !** Lancez l'application avec :
   ```bash
   ./launch_emanet.sh
   ```

## 📺 Guide d'utilisation

### Étape 1 : Trouver l'épisode sur YouTube

1. Allez sur YouTube
2. Recherchez "Emanet" et trouvez l'épisode souhaité
3. Copiez l'URL de la vidéo (Ctrl+C)

### Étape 2 : Lancer la traduction

1. Ouvrez l'application Emanet Subtitle Translator
2. Collez l'URL YouTube dans le champ prévu
3. Choisissez la qualité du modèle Whisper (transcription) :
   - **tiny** : Très rapide, qualité basique
   - **base** : Bon compromis (recommandé)
   - **small** : Meilleure qualité
   - **medium/large** : Excellente qualité (plus lent)
4. Choisissez la qualité du modèle NLLB (traduction) :
   - **small** (600M) : Rapide, bonne qualité
   - **medium** (1.3GB) : Excellente qualité (recommandé)
   - **large** (3.3GB) : Qualité maximale (nécessite beaucoup de RAM)
5. Cliquez sur "Traduire les sous-titres"
6. Attendez la fin du processus (5-20 minutes selon l'épisode)

### Étape 3 : Regarder avec VLC

1. Une fois terminé, cliquez sur "Ouvrir dans VLC"
2. VLC s'ouvrira avec la vidéo et les sous-titres français
3. Les sous-titres sont automatiquement synchronisés !

## 🔧 Dépannage

### Problème : "ModuleNotFoundError"
**Solution** : Relancez l'installation avec `bash install.sh`

### Problème : "VLC ne se lance pas"
**Solution** : 
```bash
sudo dnf install vlc
```

### Problème : "Erreur de connexion"
**Solution** : Vérifiez votre connexion Internet

### Problème : "Traduction incorrecte"
**Solution** : Essayez avec un modèle plus grand (small ou medium)

### Problème : "Sous-titres désynchronisés"
**Solution** : Dans VLC, utilisez les touches G et H pour ajuster la synchronisation

## 💡 Conseils pratiques

### Pour une meilleure qualité
- Utilisez le modèle "small" ou "medium" pour des traductions plus précises
- Les épisodes avec un son clair donnent de meilleurs résultats
- Évitez les vidéos avec de la musique forte en arrière-plan

### Pour gagner du temps
- Téléchargez plusieurs épisodes pendant la nuit
- Les sous-titres sont sauvegardés dans le dossier `emanet_subtitles/`
- Vous pouvez réutiliser les sous-titres sans refaire la traduction

### Organisation des fichiers
```
emanet_translator/
├── emanet_subtitles/       # Tous vos sous-titres traduits
│   ├── Emanet_Episode_1_FR.srt
│   ├── Emanet_Episode_2_FR.srt
│   └── ...
├── emanet_translator.py    # Application principale
├── launch_emanet.sh        # Script de lancement
└── emanet_translator.log   # Journal (pour le dépannage)
```

## 🎮 Raccourcis VLC utiles

- **Espace** : Pause/Lecture
- **F** : Plein écran
- **G** : Retarder les sous-titres
- **H** : Avancer les sous-titres
- **Ctrl + ↑/↓** : Volume
- **V** : Afficher/Masquer les sous-titres

## 📊 Temps de traitement estimés

| Durée épisode | Whisper base + NLLB small | Whisper base + NLLB medium | Whisper small + NLLB medium |
|---------------|---------------------------|----------------------------|------------------------------|
| 30 minutes    | ~15 min                   | ~20 min                    | ~30 min                      |
| 1 heure       | ~30 min                   | ~40 min                    | ~60 min                      |
| 2 heures      | ~60 min                   | ~80 min                    | ~120 min                     |

**Note** : Les temps varient selon votre processeur. Un GPU NVIDIA réduit considérablement ces temps.

## 🆘 Support

### Logs de débogage
En cas de problème, consultez le fichier `emanet_translator.log` qui contient tous les détails techniques.

### Mise à jour
Pour mettre à jour l'application :
```bash
pip install --upgrade -r requirements.txt
```

## 🌟 Fonctionnalités avancées

### Traiter plusieurs épisodes
Vous pouvez créer un script pour traiter plusieurs épisodes :
```python
# batch_process.py
urls = [
    "https://youtube.com/watch?v=...",  # Episode 1
    "https://youtube.com/watch?v=...",  # Episode 2
    # etc.
]

for url in urls:
    # L'application traitera chaque URL
    print(f"Traitement de : {url}")
```

### Sauvegarder vos préférences
Les sous-titres sont automatiquement sauvegardés et peuvent être réutilisés sans connexion Internet.

## 📝 Notes importantes

1. **Connexion Internet requise** pour le téléchargement initial des modèles et des vidéos
2. **Espace disque** : 
   - Modèles Whisper : ~500 MB à 3 GB selon la taille
   - Modèles NLLB : 600 MB (small) à 3.3 GB (large)
   - Total recommandé : 5-10 GB d'espace libre
3. **RAM recommandée** :
   - Minimum : 8 GB (pour small/small)
   - Recommandé : 16 GB (pour base/medium)
   - Optimal : 32 GB (pour large/large)
4. **Première utilisation** : Le téléchargement des modèles peut prendre 10-30 minutes. L'outil `hf_transfer` est activé automatiquement pour accélérer cette étape
5. **Qualité** : NLLB produit des traductions bien meilleures que Google Translate, surtout pour les dialogues

## 🎉 Bon visionnage !

J'espère que votre grand-mère pourra enfin profiter pleinement d'Emanet ! 

Si vous avez des questions ou des problèmes, n'hésitez pas à consulter le fichier de log ou à demander de l'aide.

---

*Développé avec amour pour permettre à tous de profiter des séries turques* ❤️