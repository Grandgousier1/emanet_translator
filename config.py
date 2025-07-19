"""
Configuration avancée pour Emanet Subtitle Translator
Modifiez ces paramètres pour personnaliser le comportement de l'application
"""

# Configuration des modèles
MODELS = {
    "whisper": {
        "default": "base",  # Modèle par défaut pour la transcription
        "device": "auto",   # "auto", "cuda", ou "cpu"
    },
    "nllb": {
        "default": "small",  # Modèle par défaut pour la traduction
        "models": {
            "small": "facebook/nllb-200-distilled-600M",
            "medium": "facebook/nllb-200-distilled-1.3B",
            "large": "facebook/nllb-200-3.3B"
        },
        "beam_size": 5,  # Nombre de beams pour la génération (qualité vs vitesse)
        "temperature": 0.9,  # Créativité de la traduction (0.5-1.0)
        "max_length": 512,  # Longueur maximale des segments
    }
}

# Configuration des langues
LANGUAGES = {
    "source": "tur_Latn",  # Turc
    "target": "fra_Latn",  # Français
}

# Configuration de l'audio
AUDIO = {
    "format": "wav",
    "quality": "192",
    "sample_rate": 16000,
}

# Configuration des sous-titres
SUBTITLES = {
    "max_line_length": 42,  # Nombre max de caractères par ligne
    "max_lines": 2,  # Nombre max de lignes par sous-titre
    "min_duration": 0.5,  # Durée minimale d'un sous-titre (secondes)
    "max_duration": 7.0,  # Durée maximale d'un sous-titre (secondes)
}

# Configuration avancée
ADVANCED = {
    "batch_size": 16,  # Taille des lots pour la traduction
    "num_workers": 4,  # Nombre de threads pour le traitement
    "cache_dir": ".cache",  # Dossier de cache pour les modèles
    "keep_temp_files": False,  # Garder les fichiers temporaires après traitement
    "log_level": "INFO",  # Niveau de log : DEBUG, INFO, WARNING, ERROR
}

# Configuration GPU (si disponible)
GPU = {
    "use_fp16": True,  # Utiliser la précision demi (économise la mémoire)
    "device_map": "auto",  # Répartition automatique sur plusieurs GPU
    "offload_folder": "offload",  # Dossier pour l'offload CPU si pas assez de VRAM
}

# Optimisations pour machines avec peu de RAM
LOW_MEMORY_MODE = {
    "enabled": False,  # Activer le mode économie de mémoire
    "batch_size": 4,  # Réduire la taille des lots
    "offload_to_disk": True,  # Décharger sur le disque si nécessaire
}
