import librosa
import numpy as np
import scipy
from hashlib import sha1
import logging

logger = logging.getLogger(__name__)

def generate_fingerprint(
    audio_path: str,
    window_duration: float = 2.0,
    step_duration: float = 0.5,
    sr: int = 22050,
    fan_value: int = 10,
) -> list[tuple[str, float]]:
    try:
        y, sr = librosa.load(audio_path, sr=sr, mono=True)
    except Exception as e:
        logger.error(f"[ERROR] Failed to load audio: {e}")
        return []

    if y is None or len(y) == 0:
        logger.error(f"[ERROR] No audio data found in: {audio_path}")
        return []

    logger.debug(f"[DEBUG] Audio loaded: {len(y) / sr:.2f}s")

    fingerprints = []
    for start in np.arange(0, len(y), step_duration * sr):
        end = int(start + window_duration * sr)
        if end > len(y):
            break
        window = y[int(start):end]
        fingerprints.extend(hashing(window, start / sr, fan_value, sr))

    logger.debug(f"[DEBUG] Total fingerprints generated: {len(fingerprints)}")
    return fingerprints

def hashing(window: np.ndarray, offset: float, fan_value: int, sr: int) -> list[tuple[str, float]]:
    hop_length = 512
    S = np.abs(librosa.stft(window, n_fft=4096, hop_length=hop_length))
    S_db = librosa.amplitude_to_db(S, ref=np.max)

    neighborhood_size = 10
    footprint = np.ones((neighborhood_size, neighborhood_size))
    local_max = (scipy.ndimage.maximum_filter(S_db, footprint.shape) == S_db)
    peaks = np.argwhere(local_max & (S_db > -30))
    peaks_sorted = sorted(peaks, key=lambda x: x[1])

    fingerprints = []
    for i in range(len(peaks_sorted)):
        for j in range(1, fan_value):
            if i + j < len(peaks_sorted):
                f1, t1 = peaks_sorted[i]
                f2, t2 = peaks_sorted[i + j]
                delta_t = t2 - t1
                if 0 < delta_t <= 200:
                    h = sha1(f"{f1}|{f2}|{delta_t}".encode()).hexdigest()[:20]
                    time_offset = t1 * hop_length / sr + offset
                    fingerprints.append((h, float(time_offset)))
    return fingerprints

