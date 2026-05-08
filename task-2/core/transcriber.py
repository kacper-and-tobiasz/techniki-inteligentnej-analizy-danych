import core.ffmpeg_setup as _
import whisper
from PySide6.QtCore import QThread, Signal
LANGUAGE_NAMES = {'pl': 'Polski', 'en': 'English', 'de': 'Deutsch', 'es': 'Español'}
WHISPER_MODELS = ['tiny', 'base', 'small', 'medium', 'large']

def get_language_display(lang_code: str) -> str:
    if lang_code in LANGUAGE_NAMES:
        return LANGUAGE_NAMES[lang_code]
    return lang_code
_model_cache = {}

def get_model(model_name: str):
    if model_name not in _model_cache:
        _model_cache[model_name] = whisper.load_model(model_name)
    return _model_cache[model_name]

class TranscriberThread(QThread):
    finished = Signal(str, str, dict)
    progress = Signal(str)
    error = Signal(str)

    def __init__(self, audio_path: str, model_name: str='base'):
        super().__init__()
        self.audio_path = audio_path
        self.model_name = model_name

    def run(self):
        self.progress.emit('Ładowanie modelu Whisper...')
        model = get_model(self.model_name)
        self.progress.emit('Wykrywanie języka...')
        audio = whisper.load_audio(self.audio_path)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio, n_mels=model.dims.n_mels).to(model.device)
        _, probs = model.detect_language(mel)
        filtered_probs = {k: v for k, v in probs.items() if k in LANGUAGE_NAMES}
        detected_lang = max(filtered_probs, key=filtered_probs.get)
        top_langs = dict(sorted(filtered_probs.items(), key=lambda x: x[1], reverse=True))
        self.progress.emit(f'Transkrypcja ({get_language_display(detected_lang)})...')
        result = model.transcribe(self.audio_path, language=detected_lang, fp16=False)
        text = result['text'].strip()
        self.finished.emit(text, detected_lang, top_langs)