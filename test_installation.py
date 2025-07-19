#!/usr/bin/env python3
"""
Script de test pour vérifier l'installation d'Emanet Subtitle Translator
"""

import sys
import subprocess
from pathlib import Path

def test_import(module_name):
    """Teste l'importation d'un module"""
    try:
        __import__(module_name)
        print(f"✓ {module_name} installé correctement")
        return True
    except ImportError:
        print(f"✗ {module_name} n'est pas installé")
        return False

def test_command(command):
    """Teste la disponibilité d'une commande système"""
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)
        print(f"✓ {command} disponible")
        return True
    except:
        print(f"✗ {command} non disponible")
        return False

def main():
    print("=== Test d'installation Emanet Subtitle Translator ===\n")
    
    all_ok = True
    
    # Test des modules Python
    print("1. Vérification des modules Python :")
    modules = ["yt_dlp", "whisper", "transformers", "accelerate", "srt", "torch", "tkinter"]
    for module in modules:
        if not test_import(module):
            all_ok = False
    
    print("\n2. Vérification des commandes système :")
    commands = ["ffmpeg", "vlc"]
    for command in commands:
        if not test_command(command):
            all_ok = False
    
    print("\n3. Vérification des dossiers :")
    folders = ["emanet_subtitles", "temp"]
    for folder in folders:
        path = Path(folder)
        if path.exists():
            print(f"✓ Dossier '{folder}' existe")
        else:
            print(f"✗ Dossier '{folder}' manquant")
            path.mkdir(exist_ok=True)
            print(f"  → Créé automatiquement")
    
    print("\n4. Test de Whisper :")
    try:
        import whisper
        print("✓ Whisper peut être importé")
        print("  Note : Le modèle sera téléchargé lors de la première utilisation")
    except Exception as e:
        print(f"✗ Problème avec Whisper : {e}")
        all_ok = False
    
    print("\n5. Test de NLLB (traduction) :")
    try:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        print("✓ Transformers (NLLB) peut être importé")
        print("  Note : Le modèle de traduction sera téléchargé lors de la première utilisation")
        
        # Vérifier CUDA si disponible
        import torch
        if torch.cuda.is_available():
            print(f"✓ GPU CUDA détecté : {torch.cuda.get_device_name(0)}")
            print("  Les traductions seront plus rapides avec le GPU")
        else:
            print("  GPU non détecté - Utilisation du CPU (plus lent)")
    except Exception as e:
        print(f"✗ Problème avec Transformers : {e}")
        all_ok = False
    
    print("\n" + "="*50)
    if all_ok:
        print("✅ Tout est correctement installé !")
        print("\nVous pouvez lancer l'application avec : ./launch_emanet.sh")
    else:
        print("❌ Des problèmes ont été détectés.")
        print("\nRelancez l'installation avec : bash install.sh")
    
    print("\nConseils :")
    print("- Pour la première utilisation, prévoyez une connexion Internet stable")
    print("- Le téléchargement du modèle Whisper peut prendre quelques minutes")
    print("- Commencez avec le modèle 'base' pour tester")

if __name__ == "__main__":
    main()
