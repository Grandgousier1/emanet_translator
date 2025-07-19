#!/usr/bin/env python3
"""
Emanet Subtitle Translator
Traduit automatiquement les dialogues turcs de la série Emanet en sous-titres français
"""

import os
import sys
import json
import subprocess
import logging
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import queue

# Bibliothèques externes
try:
    import yt_dlp
    import whisper
    import srt
    from datetime import timedelta
    import torch
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
except ImportError as e:
    print(f"Erreur d'importation : {e}")
    print("Installez les dépendances avec : pip install -r requirements.txt")
    sys.exit(1)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('emanet_translator.log'),
        logging.StreamHandler()
    ]
)

class EmanetTranslator:
    def __init__(self):
        self.whisper_model = None
        self.translation_model = None
        self.tokenizer = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.output_dir = Path("emanet_subtitles")
        self.output_dir.mkdir(exist_ok=True)
        self.temp_dir = Path("temp")
        self.temp_dir.mkdir(exist_ok=True)
        
    def load_whisper_model(self, model_size="base"):
        """Charge le modèle Whisper pour la reconnaissance vocale"""
        logging.info(f"Chargement du modèle Whisper '{model_size}'...")
        try:
            self.whisper_model = whisper.load_model(model_size)
            logging.info("Modèle Whisper chargé avec succès")
            return True
        except Exception as e:
            logging.error(f"Erreur lors du chargement du modèle : {e}")
            return False
    
    def load_translation_model(self, model_size="small"):
        """Charge le modèle NLLB pour la traduction"""
        logging.info(f"Chargement du modèle de traduction NLLB '{model_size}'...")
        
        # Mapping des tailles de modèles NLLB
        model_names = {
            "small": "facebook/nllb-200-distilled-600M",  # 600M params - Rapide
            "medium": "facebook/nllb-200-distilled-1.3B",  # 1.3B params - Équilibré
            "large": "facebook/nllb-200-3.3B"  # 3.3B params - Meilleure qualité
        }
        
        model_name = model_names.get(model_size, model_names["small"])
        
        try:
            # Charger le tokenizer et le modèle
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.translation_model = AutoModelForSeq2SeqLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
            ).to(self.device)
            
            logging.info(f"Modèle NLLB chargé avec succès sur {self.device}")
            return True
            
        except Exception as e:
            logging.error(f"Erreur lors du chargement du modèle NLLB : {e}")
            return False
    
    def download_video(self, youtube_url, progress_callback=None):
        """Télécharge la vidéo YouTube et extrait l'audio"""
        logging.info(f"Téléchargement de : {youtube_url}")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(self.temp_dir / '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [self._download_progress_hook] if progress_callback else []
        }
        
        self.progress_callback = progress_callback
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=True)
                video_title = info['title']
                audio_file = self.temp_dir / f"{video_title}.wav"
                
                if not audio_file.exists():
                    # Chercher le fichier audio généré
                    for file in self.temp_dir.glob("*.wav"):
                        audio_file = file
                        break
                
                logging.info(f"Audio extrait : {audio_file}")
                return audio_file, video_title
                
        except Exception as e:
            logging.error(f"Erreur lors du téléchargement : {e}")
            raise
    
    def _download_progress_hook(self, d):
        if d['status'] == 'downloading' and self.progress_callback:
            percent = d.get('_percent_str', '0%').strip('%')
            try:
                self.progress_callback(float(percent))
            except:
                pass
    
    def transcribe_audio(self, audio_file, progress_callback=None):
        """Transcrit l'audio turc en texte avec timestamps"""
        logging.info(f"Transcription de : {audio_file}")
        
        if not self.whisper_model:
            raise Exception("Le modèle Whisper n'est pas chargé")
        
        try:
            # Transcription avec Whisper
            result = self.whisper_model.transcribe(
                str(audio_file),
                language="tr",  # Turc
                task="transcribe",
                verbose=False
            )
            
            # Extraire les segments avec timestamps
            segments = []
            for segment in result['segments']:
                segments.append({
                    'start': segment['start'],
                    'end': segment['end'],
                    'text': segment['text'].strip()
                })
            
            logging.info(f"Transcription terminée : {len(segments)} segments")
            return segments
            
        except Exception as e:
            logging.error(f"Erreur lors de la transcription : {e}")
            raise
    
    def translate_segments(self, segments, progress_callback=None):
        """Traduit les segments du turc vers le français avec NLLB"""
        logging.info(f"Traduction de {len(segments)} segments...")
        
        if not self.translation_model or not self.tokenizer:
            raise Exception("Le modèle de traduction n'est pas chargé")
        
        translated_segments = []
        
        # Codes de langue pour NLLB
        src_lang = "tur_Latn"  # Turc
        tgt_lang = "fra_Latn"  # Français
        
        for i, segment in enumerate(segments):
            try:
                # Préparer le texte pour la traduction
                text = segment['text']
                
                # Tokenizer avec le code de langue source
                self.tokenizer.src_lang = src_lang
                inputs = self.tokenizer(
                    text,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=512
                ).to(self.device)
                
                # Générer la traduction
                with torch.no_grad():
                    translated_tokens = self.translation_model.generate(
                        **inputs,
                        forced_bos_token_id=self.tokenizer.lang_code_to_id[tgt_lang],
                        max_new_tokens=512,
                        num_beams=5,
                        temperature=0.9,
                        do_sample=False
                    )
                
                # Décoder la traduction
                translation = self.tokenizer.decode(
                    translated_tokens[0],
                    skip_special_tokens=True
                )
                
                translated_segments.append({
                    'start': segment['start'],
                    'end': segment['end'],
                    'text': translation
                })
                
                if progress_callback:
                    progress_callback((i + 1) / len(segments) * 100)
                
            except Exception as e:
                logging.warning(f"Erreur de traduction pour le segment {i}: {e}")
                # En cas d'erreur, garder le texte original
                translated_segments.append({
                    'start': segment['start'],
                    'end': segment['end'],
                    'text': f"[TR] {segment['text']}"
                })
        
        logging.info("Traduction terminée")
        return translated_segments
    
    def create_srt_file(self, segments, output_filename):
        """Crée un fichier SRT à partir des segments traduits"""
        logging.info(f"Création du fichier SRT : {output_filename}")
        
        srt_segments = []
        for i, segment in enumerate(segments, 1):
            srt_segment = srt.Subtitle(
                index=i,
                start=timedelta(seconds=segment['start']),
                end=timedelta(seconds=segment['end']),
                content=segment['text']
            )
            srt_segments.append(srt_segment)
        
        # Écrire le fichier SRT
        srt_content = srt.compose(srt_segments)
        output_path = self.output_dir / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        
        logging.info(f"Fichier SRT créé : {output_path}")
        return output_path
    
    def process_video(self, youtube_url, model_size="base", translation_model_size="small", progress_callback=None):
        """Processus complet : téléchargement -> transcription -> traduction -> SRT"""
        try:
            # 1. Charger le modèle Whisper si nécessaire
            if not self.whisper_model:
                if progress_callback:
                    progress_callback("Chargement du modèle Whisper...", 0)
                self.load_whisper_model(model_size)
            
            # 2. Charger le modèle de traduction si nécessaire
            if not self.translation_model:
                if progress_callback:
                    progress_callback("Chargement du modèle de traduction NLLB...", 5)
                self.load_translation_model(translation_model_size)
            
            # 3. Télécharger la vidéo
            if progress_callback:
                progress_callback("Téléchargement de la vidéo...", 10)
            audio_file, video_title = self.download_video(youtube_url)
            
            # 4. Transcrire l'audio
            if progress_callback:
                progress_callback("Transcription audio...", 30)
            segments = self.transcribe_audio(audio_file)
            
            # 5. Traduire les segments
            if progress_callback:
                progress_callback("Traduction en français...", 60)
            translated_segments = self.translate_segments(segments)
            
            # 6. Créer le fichier SRT
            if progress_callback:
                progress_callback("Création des sous-titres...", 90)
            safe_title = "".join(c for c in video_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            srt_filename = f"{safe_title}_FR.srt"
            srt_path = self.create_srt_file(translated_segments, srt_filename)
            
            # 7. Nettoyer les fichiers temporaires
            if audio_file.exists():
                audio_file.unlink()
            
            if progress_callback:
                progress_callback("Terminé !", 100)
            
            return srt_path
            
        except Exception as e:
            logging.error(f"Erreur dans le processus : {e}")
            raise
    
    def open_in_vlc(self, video_url, srt_path):
        """Ouvre la vidéo YouTube dans VLC avec les sous-titres"""
        try:
            # Commande VLC pour Fedora
            vlc_cmd = [
                "vlc",
                video_url,
                f"--sub-file={srt_path}",
                "--sub-track=0"
            ]
            
            subprocess.Popen(vlc_cmd)
            logging.info(f"VLC lancé avec la vidéo et les sous-titres")
            
        except Exception as e:
            logging.error(f"Erreur lors du lancement de VLC : {e}")
            raise


class EmanetGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Emanet Subtitle Translator")
        self.root.geometry("800x600")
        
        self.translator = EmanetTranslator()
        self.processing = False
        self.queue = queue.Queue()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        title_label = ttk.Label(
            main_frame, 
            text="Traducteur de sous-titres Emanet", 
            font=('Arial', 18, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Instructions
        info_label = ttk.Label(
            main_frame,
            text="Collez l'URL YouTube de l'épisode d'Emanet à traduire :",
            font=('Arial', 12)
        )
        info_label.pack(pady=(0, 10))
        
        # URL Entry
        url_frame = ttk.Frame(main_frame)
        url_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.url_entry = ttk.Entry(url_frame, font=('Arial', 11))
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.paste_button = ttk.Button(
            url_frame,
            text="Coller",
            command=self.paste_url
        )
        self.paste_button.pack(side=tk.RIGHT)
        
        # Options
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Modèle Whisper
        model_label = ttk.Label(options_frame, text="Modèle Whisper :")
        model_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.model_var = tk.StringVar(value="base")
        model_combo = ttk.Combobox(
            options_frame,
            textvariable=self.model_var,
            values=["tiny", "base", "small", "medium", "large"],
            state="readonly",
            width=10
        )
        model_combo.grid(row=0, column=1, sticky=tk.W)
        
        model_info = ttk.Label(
            options_frame,
            text="(Plus grand = plus précis mais plus lent)",
            font=('Arial', 9, 'italic')
        )
        model_info.grid(row=0, column=2, padx=(10, 0))
        
        # Modèle de traduction NLLB
        translation_label = ttk.Label(options_frame, text="Modèle traduction :")
        translation_label.grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        self.translation_var = tk.StringVar(value="small")
        translation_combo = ttk.Combobox(
            options_frame,
            textvariable=self.translation_var,
            values=["small", "medium", "large"],
            state="readonly",
            width=10
        )
        translation_combo.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        translation_info = ttk.Label(
            options_frame,
            text="(small=600M, medium=1.3GB, large=3.3GB)",
            font=('Arial', 9, 'italic')
        )
        translation_info.grid(row=1, column=2, padx=(10, 0), pady=(10, 0))
        
        # Boutons d'action
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(0, 20))
        
        self.process_button = ttk.Button(
            button_frame,
            text="Traduire les sous-titres",
            command=self.start_processing,
            style='Accent.TButton'
        )
        self.process_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.vlc_button = ttk.Button(
            button_frame,
            text="Ouvrir dans VLC",
            command=self.open_in_vlc,
            state=tk.DISABLED
        )
        self.vlc_button.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Prêt", font=('Arial', 10))
        self.status_label.pack()
        
        # Log text
        log_frame = ttk.LabelFrame(main_frame, text="Journal", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_frame, height=10, font=('Courier', 9))
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Variables
        self.current_srt_path = None
        self.current_video_url = None
        
    def paste_url(self):
        """Colle l'URL du presse-papiers"""
        try:
            url = self.root.clipboard_get()
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, url)
        except:
            pass
    
    def log(self, message):
        """Ajoute un message au journal"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def update_progress(self, message, value):
        """Met à jour la barre de progression"""
        self.status_label.config(text=message)
        self.progress_var.set(value)
        self.root.update()
    
    def start_processing(self):
        """Lance le processus de traduction dans un thread séparé"""
        if self.processing:
            return
        
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Erreur", "Veuillez entrer une URL YouTube")
            return
        
        if "youtube.com" not in url and "youtu.be" not in url:
            messagebox.showerror("Erreur", "L'URL doit être une vidéo YouTube")
            return
        
        self.processing = True
        self.process_button.config(state=tk.DISABLED)
        self.vlc_button.config(state=tk.DISABLED)
        self.current_video_url = url
        
        # Lancer dans un thread
        thread = threading.Thread(target=self.process_video_thread, args=(url,))
        thread.daemon = True
        thread.start()
    
    def process_video_thread(self, url):
        """Thread de traitement de la vidéo"""
        try:
            self.log(f"Début du traitement de : {url}")
            
            def progress_callback(message, value=None):
                if isinstance(message, (int, float)):
                    # C'est une valeur de progression
                    self.queue.put(("progress", "", message))
                else:
                    # C'est un message avec valeur
                    self.queue.put(("progress", message, value))
            
            # Lancer le traitement
            srt_path = self.translator.process_video(
                url,
                model_size=self.model_var.get(),
                translation_model_size=self.translation_var.get(),
                progress_callback=progress_callback
            )
            
            self.current_srt_path = srt_path
            self.queue.put(("complete", str(srt_path)))
            
        except Exception as e:
            self.queue.put(("error", str(e)))
        
        finally:
            self.processing = False
    
    def open_in_vlc(self):
        """Ouvre la vidéo dans VLC avec les sous-titres"""
        if not self.current_srt_path or not self.current_video_url:
            return
        
        try:
            self.translator.open_in_vlc(self.current_video_url, self.current_srt_path)
            self.log("VLC lancé avec les sous-titres")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de lancer VLC : {e}")
    
    def check_queue(self):
        """Vérifie la file des messages du thread"""
        try:
            while True:
                msg_type, *args = self.queue.get_nowait()
                
                if msg_type == "progress":
                    if len(args) == 2:
                        self.update_progress(args[0], args[1])
                    else:
                        self.progress_var.set(args[0])
                
                elif msg_type == "complete":
                    srt_path = args[0]
                    self.log(f"Sous-titres créés : {srt_path}")
                    self.status_label.config(text="Traduction terminée !")
                    self.progress_var.set(100)
                    self.process_button.config(state=tk.NORMAL)
                    self.vlc_button.config(state=tk.NORMAL)
                    messagebox.showinfo(
                        "Succès", 
                        f"Les sous-titres ont été créés !\n\n{srt_path}\n\n" +
                        "Cliquez sur 'Ouvrir dans VLC' pour regarder la vidéo."
                    )
                
                elif msg_type == "error":
                    error_msg = args[0]
                    self.log(f"Erreur : {error_msg}")
                    self.status_label.config(text="Erreur lors du traitement")
                    self.process_button.config(state=tk.NORMAL)
                    messagebox.showerror("Erreur", f"Une erreur s'est produite :\n\n{error_msg}")
                
        except queue.Empty:
            pass
        
        # Replanifier la vérification
        self.root.after(100, self.check_queue)
    
    def run(self):
        """Lance l'application"""
        self.log("Application démarrée")
        self.log(f"Dossier de sortie : {self.translator.output_dir}")
        self.check_queue()
        self.root.mainloop()


def main():
    """Point d'entrée principal"""
    app = EmanetGUI()
    app.run()


if __name__ == "__main__":
    main()
