from subprocess import CalledProcessError, run

import imageio_ffmpeg
import numpy as np
import whisper
import whisper.audio as whisper_audio


def _install() -> None:
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    def load_audio(file: str, sr: int = whisper_audio.SAMPLE_RATE):
        cmd = [
            ffmpeg_exe,
            "-nostdin",
            "-threads",
            "0",
            "-i",
            file,
            "-f",
            "s16le",
            "-ac",
            "1",
            "-acodec",
            "pcm_s16le",
            "-ar",
            str(sr),
            "-",
        ]
        try:
            out = run(cmd, capture_output=True, check=True).stdout
        except CalledProcessError as e:
            raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e

        return np.frombuffer(out, np.int16).flatten().astype(np.float32) / 32768.0

    load_audio.__doc__ = whisper_audio.load_audio.__doc__
    whisper_audio.load_audio = load_audio
    whisper.load_audio = load_audio


_install()
