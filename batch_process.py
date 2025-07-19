#!/usr/bin/env python3
"""
Script de traitement par lot pour Emanet Subtitle Translator
Permet de traduire plusieurs épisodes automatiquement
"""

import sys
import time
from pathlib import Path

# Importer le traducteur principal
try:
    from emanet_translator import EmanetTranslator
except ImportError:
    print("Erreur : emanet_translator.py non trouvé dans le dossier")
    sys.exit(1)

# Liste des URLs YouTube des épisodes à traduire
# Remplacez ces URLs par les vrais liens des épisodes
EPISODES = [
    # Exemple :
    # "https://www.youtube.com/watch?v=XXXXXXXXXX",  # Episode 1
    # "https://www.youtube.com/watch?v=XXXXXXXXXX",  # Episode 2
    # "https://www.youtube.com/watch?v=XXXXXXXXXX",  # Episode 3
]

def main():
    """Traite tous les épisodes de la liste"""
    
    if not EPISODES:
        print("⚠️  Aucun épisode à traiter !")
        print("")
        print("Modifiez ce fichier et ajoutez les URLs YouTube dans la liste EPISODES")
        print("Exemple :")
        print('EPISODES = [')
        print('    "https://www.youtube.com/watch?v=ABC123",  # Episode 1')
        print('    "https://www.youtube.com/watch?v=DEF456",  # Episode 2')
        print(']')
        return
    
    print(f"=== Traitement par lot de {len(EPISODES)} épisodes ===\n")
    
    # Créer le traducteur
    translator = EmanetTranslator()
    
    # Charger le modèle une seule fois
    print("Chargement du modèle Whisper...")
    translator.load_whisper_model("base")  # Vous pouvez changer pour "small" ou "medium"
    print("✓ Modèle Whisper chargé\n")
    
    print("Chargement du modèle de traduction NLLB...")
    translator.load_translation_model("medium")  # Vous pouvez changer pour "small" ou "large"
    print("✓ Modèle NLLB chargé\n")
    
    # Traiter chaque épisode
    successful = 0
    failed = 0
    
    for i, url in enumerate(EPISODES, 1):
        print(f"--- Episode {i}/{len(EPISODES)} ---")
        print(f"URL : {url}")
        
        try:
            # Traiter l'épisode
            start_time = time.time()
            
            def progress_callback(message, value=None):
                if isinstance(message, str) and value is not None:
                    print(f"{message} ({value}%)")
            
            srt_path = translator.process_video(url, progress_callback=progress_callback)
            
            elapsed = time.time() - start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            
            print(f"✓ Terminé en {minutes}m {seconds}s")
            print(f"✓ Sous-titres : {srt_path}\n")
            successful += 1
            
        except Exception as e:
            print(f"✗ Erreur : {e}\n")
            failed += 1
            continue
        
        # Pause entre les épisodes pour éviter la surcharge
        if i < len(EPISODES):
            print("Pause de 10 secondes avant le prochain épisode...")
            time.sleep(10)
    
    # Résumé
    print("\n=== Résumé ===")
    print(f"✓ Réussis : {successful}")
    print(f"✗ Échoués : {failed}")
    print(f"\nLes sous-titres sont dans : {translator.output_dir}/")
    
    if successful > 0:
        print("\nVous pouvez maintenant ouvrir VLC et charger manuellement")
        print("la vidéo YouTube avec son fichier de sous-titres .srt")


if __name__ == "__main__":
    main()
