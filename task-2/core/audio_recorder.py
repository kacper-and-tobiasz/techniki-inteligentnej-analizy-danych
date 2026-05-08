import os
import tempfile
import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wav
from PySide6.QtCore import QThread, Signal

class AudioRecorderThread(QThread):
    finished = Signal(str)
    error = Signal(str)
    level_changed = Signal(float)

    def __init__(self, sample_rate=16000):
        super().__init__()
        self.sample_rate = sample_rate
        self.is_recording = False
        self.frames = []

    def run(self):
        self.is_recording = True
        self.frames = []
        
        def callback(indata, frames, time_info, status):
            if self.is_recording:
                self.frames.append(indata.copy())
                level = np.sqrt(np.mean(indata ** 2))
                self.level_changed.emit(min(float(level) * 10, 1.0))

        with sd.InputStream(samplerate=self.sample_rate, channels=1, dtype='float32', callback=callback, blocksize=1024):
            while self.is_recording:
                sd.sleep(50)

        if self.frames:
            audio_data = np.concatenate(self.frames, axis=0)
            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                audio_data = audio_data / max_val * 0.95
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, 'recipe_voice_recording.wav')
            wav.write(temp_path, self.sample_rate, (audio_data * 32767).astype(np.int16))
            self.finished.emit(temp_path)
        else:
            self.error.emit('Nie nagrano żadnego dźwięku.')

    def stop(self):
        self.is_recording = False