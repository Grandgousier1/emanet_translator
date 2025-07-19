#!/bin/bash

# Script d'installation du support CUDA pour Emanet Subtitle Translator
# Optionnel - seulement si vous avez un GPU NVIDIA

echo "=== Installation du support GPU NVIDIA ==="
echo ""

# Vérifier la présence d'un GPU NVIDIA
if ! command -v nvidia-smi &> /dev/null; then
    echo "❌ Aucun GPU NVIDIA détecté."
    echo "Ce script n'est utile que si vous avez une carte graphique NVIDIA."
    exit 1
fi

echo "GPU détecté :"
nvidia-smi --query-gpu=name --format=csv,noheader
echo ""

# Activer l'environnement virtuel
if [ ! -d "venv" ]; then
    echo "❌ L'environnement virtuel n'existe pas."
    echo "Lancez d'abord : bash install.sh"
    exit 1
fi

source venv/bin/activate

echo "Installation de PyTorch avec support CUDA..."
echo "Cela peut prendre plusieurs minutes..."
echo ""

# Désinstaller l'ancienne version CPU de PyTorch
pip uninstall -y torch torchvision torchaudio

# Installer PyTorch avec CUDA 11.8 (compatible avec la plupart des GPU récents)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

echo ""
echo "Test du support CUDA..."

# Tester CUDA
python3 -c "
import torch
if torch.cuda.is_available():
    print('✅ CUDA est disponible !')
    print(f'   GPU : {torch.cuda.get_device_name(0)}')
    print(f'   Mémoire : {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')
else:
    print('❌ CUDA n\'est pas disponible')
"

echo ""
echo "=== Installation terminée ==="
echo ""
echo "Avec le GPU, les traductions seront :"
echo "- 5 à 10 fois plus rapides"
echo "- Possibilité d'utiliser les modèles 'large' confortablement"
echo "- Consommation CPU réduite"
echo ""
echo "Configuration recommandée avec GPU :"
echo "- Whisper : 'small' ou 'medium'"
echo "- NLLB : 'medium' ou 'large'"
