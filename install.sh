#!/bin/bash

# Script d'installation pour Emanet Subtitle Translator sur Fedora 41
# Exécuter avec : bash install.sh (sans sudo!)

set -e

echo "=== Installation d'Emanet Subtitle Translator ==="
echo ""

# Vérifier qu'on n'est PAS root
if [ "$EUID" -eq 0 ]; then 
   echo "⚠️  Ne lancez pas ce script avec sudo !"
   echo "Utilisez simplement : bash install.sh"
   exit 1
fi

# Couleurs pour l'affichage
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Fonction pour afficher les succès
success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Fonction pour afficher les erreurs
error() {
    echo -e "${RED}✗ $1${NC}"
    exit 1
}

# Vérifier qu'on est sur Fedora
if ! command -v dnf &> /dev/null; then
    error "Ce script est conçu pour Fedora. DNF n'est pas disponible."
fi

echo "1. Installation des dépendances système..."
echo ""

# Installer les dépendances système
echo "Installation des paquets manquants..."
PACKAGES=(
    "python3"
    "python3-pip"
    "python3-tkinter"
    "ffmpeg"
    "ffmpeg-free-libs"
    "vlc"
    "git"
    "gcc"
    "gcc-c++"
    "python3-devel"
)

for package in "${PACKAGES[@]}"; do
    if ! rpm -q "$package" &> /dev/null; then
        echo "Installation de $package..."
        sudo dnf install -y "$package" || {
            # Si le paquet n'existe pas, essayer des alternatives
            if [ "$package" = "ffmpeg-free-libs" ]; then
                echo "Tentative avec ffmpeg-libs..."
                sudo dnf install -y ffmpeg-libs 2>/dev/null || echo "Paquet ffmpeg-libs non trouvé, ignoré"
            else
                error "Impossible d'installer $package"
            fi
        }
    else
        echo "✓ $package déjà installé"
    fi
done

success "Dépendances système installées"

echo ""
echo "2. Mise à jour de pip..."
python3 -m pip install --upgrade pip --user || error "Échec de la mise à jour de pip"
success "Pip mis à jour"

echo ""
echo "3. Installation des dépendances Python..."
echo "Cela peut prendre plusieurs minutes pour télécharger les modèles..."
echo ""

# Créer un environnement virtuel (recommandé)
echo "Création de l'environnement virtuel..."
python3 -m venv venv || error "Échec de la création de l'environnement virtuel"
success "Environnement virtuel créé"

# Activer l'environnement virtuel
source venv/bin/activate || error "Échec de l'activation de l'environnement virtuel"
success "Environnement virtuel activé"

# Installer les dépendances Python
pip install -r requirements.txt || error "Échec de l'installation des dépendances Python"
success "Dépendances Python installées"

echo ""
echo "4. Téléchargement du modèle Whisper de base..."
echo "Le modèle sera téléchargé lors de la première utilisation"
echo ""

# Créer les dossiers nécessaires
mkdir -p emanet_subtitles
mkdir -p temp
success "Dossiers créés"

# Créer un script de lancement
cat > launch_emanet.sh << 'EOF'
#!/bin/bash
# Script de lancement pour Emanet Subtitle Translator

# Activer l'environnement virtuel
source venv/bin/activate

# Accélérer les téléchargements Hugging Face
export HF_HUB_ENABLE_HF_TRANSFER=1

# Lancer l'application
python3 emanet_translator.py
EOF

chmod +x launch_emanet.sh
success "Script de lancement créé"

# Créer un fichier desktop pour le menu d'applications
cat > emanet-translator.desktop << EOF
[Desktop Entry]
Name=Emanet Subtitle Translator
Comment=Traduit les sous-titres de la série Emanet
Exec=$(pwd)/launch_emanet.sh
Icon=$(pwd)/icon.png
Terminal=false
Type=Application
Categories=AudioVideo;Video;
EOF

# Installer le fichier desktop
if [ -d "$HOME/.local/share/applications" ]; then
    cp emanet-translator.desktop "$HOME/.local/share/applications/"
    success "Raccourci ajouté au menu d'applications"
fi

echo ""
echo "=== Installation terminée avec succès ! ==="
echo ""
echo "Pour lancer l'application :"
echo "  1. Depuis le terminal : ./launch_emanet.sh"
echo "  2. Depuis le menu d'applications : cherchez 'Emanet'"
echo ""
echo "Notes importantes :"
echo "- Le premier lancement téléchargera les modèles IA :"
echo "  • Modèle Whisper : ~140 MB à 1 GB selon la taille"
echo "  • Modèle NLLB : ~600 MB à 3.3 GB selon la taille"
echo "- Assurez-vous d'avoir une connexion Internet active"
echo "- Les sous-titres seront sauvegardés dans : emanet_subtitles/"
echo ""
echo "Configuration recommandée :"
echo "- Pour de meilleurs résultats, utilisez Whisper 'base' + NLLB 'medium'"
echo "- Si vous avez un GPU NVIDIA, les traductions seront beaucoup plus rapides"
echo ""

# Test de VLC
if command -v vlc &> /dev/null; then
    success "VLC est installé et prêt"
else
    error "VLC n'est pas correctement installé"
fi

# Test GPU NVIDIA
if command -v nvidia-smi &> /dev/null; then
    echo ""
    success "GPU NVIDIA détecté ! Les traductions seront accélérées."
    echo "Pour activer CUDA, installez : pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
fi

echo ""
echo "Bon visionnage à votre grand-mère ! 🎬"
