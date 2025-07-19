# Guide : Optimisation pour les ordinateurs avec peu de RAM

## 💾 Configuration minimale

Si votre ordinateur a **8 GB de RAM ou moins**, suivez ces conseils :

### 1. **Configuration recommandée**

```
Whisper : tiny
NLLB : small
```

Cette configuration :
- Utilise environ 4-6 GB de RAM
- Produit toujours de bonnes traductions
- Fonctionne sur la plupart des ordinateurs

### 2. **Fermer les autres applications**

Avant de lancer la traduction :
- Fermez votre navigateur web
- Fermez les autres applications
- Désactivez temporairement l'antivirus (le réactiver après)

### 3. **Traiter des épisodes plus courts**

Si un épisode complet est trop lourd :
- Téléchargez l'épisode en plusieurs parties
- Traduisez chaque partie séparément
- Les sous-titres peuvent être combinés après

### 4. **Utiliser le mode batch la nuit**

Le script `batch_process.py` peut traiter plusieurs épisodes pendant que vous dormez :
- L'ordinateur a toute la RAM disponible
- Pas besoin de surveiller
- Tous les sous-titres seront prêts au matin

## 🚀 Optimisations avancées

### Mode économie de mémoire

Créez un fichier `low_memory_mode.py` :

```python
#!/usr/bin/env python3
import os
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:512"

# Importer et lancer l'application normale
from emanet_translator import main
main()
```

### Augmenter la mémoire virtuelle (swap)

Sur Fedora :
```bash
# Créer un fichier swap de 8 GB
sudo dd if=/dev/zero of=/swapfile bs=1G count=8
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Utiliser les modèles quantifiés

Les modèles quantifiés utilisent 2-4x moins de mémoire :
- Légère perte de qualité (5-10%)
- Beaucoup plus rapides
- Parfaits pour les vieux ordinateurs

## 📊 Tableau de consommation mémoire

| Configuration | RAM utilisée | Qualité | Vitesse |
|--------------|--------------|---------|---------|
| tiny + small | 4-5 GB | Bonne | Rapide |
| base + small | 6-7 GB | Très bonne | Normale |
| base + medium | 10-12 GB | Excellente | Normale |
| small + medium | 12-14 GB | Excellente | Lente |
| small + large | 18-20 GB | Parfaite | Très lente |

## 🆘 Erreurs courantes

### "CUDA out of memory"
**Solution** : Utilisez un modèle plus petit ou désactivez le GPU

### "Killed" ou "MemoryError"
**Solution** : 
1. Utilisez une configuration plus légère
2. Augmentez le swap
3. Fermez toutes les autres applications

### "Loading checkpoint shards"
**Normal** : Le modèle se charge par morceaux, patientez

## 💡 Astuce finale

Pour les très vieux ordinateurs (4 GB RAM) :
1. Utilisez Google Colab (gratuit avec GPU)
2. Ou louez un serveur cloud temporaire
3. Ou demandez à un ami avec un meilleur PC

La qualité NLLB vaut l'effort supplémentaire ! 🎯
