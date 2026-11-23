import math
import sys
import time


SAMPLE_RATE = 16000
BLOCK_SIZE = 1024
MAX_RECORD_SECONDS = 60
MAX_INITIAL_SILENCE_SECONDS = 8
END_SILENCE_SECONDS = 0.9


def record_utterance(np, sounddevice):
    audio_blocks = []
    started_at = time.monotonic()
    speech_started = False
    silence_seconds = 0.0
    noise_floor = 0.001

    with sounddevice.InputStream(
            samplerate=SAMPLE_RATE, channels=1, dtype="float32",
            blocksize=BLOCK_SIZE) as stream:
        while time.monotonic() - started_at < MAX_RECORD_SECONDS:
            block, _ = stream.read(BLOCK_SIZE)
            samples = np.asarray(block, dtype=np.float32).reshape(-1)
            if samples.size == 0:
                continue
            audio_blocks.append(samples)
            level = math.sqrt(float(np.mean(np.square(samples))))
            elapsed = time.monotonic() - started_at

            if not speech_started:
                threshold = max(0.004, min(0.010, noise_floor * 2.0))
                if level >= threshold:
                    speech_started = True
                elif elapsed <= 0.5 and level < 0.008:
                    noise_floor = min(0.005, noise_floor * 0.9 + level * 0.1)
            else:
                silence_threshold = max(0.004, min(0.010, noise_floor * 2.0))
                if level < silence_threshold:
                    silence_seconds += BLOCK_SIZE / SAMPLE_RATE
                    if silence_seconds >= END_SILENCE_SECONDS:
                        break
                else:
                    silence_seconds = 0.0

            if not speech_started and elapsed >= MAX_INITIAL_SILENCE_SECONDS:
                return None

    if not speech_started:
        return None
    audio = np.concatenate(audio_blocks)
    if audio.size < SAMPLE_RATE // 4:
        return None
    return audio


def main():
    if len(sys.argv) != 2:
        print("Whisper-Modellpfad fehlt.", file=sys.stderr)
        return 1

    try:
        import numpy as np
        import sounddevice
        from faster_whisper import WhisperModel
    except ImportError as error:
        print(f"Whisper-Abhängigkeit fehlt: {error}", file=sys.stderr)
        return 1

    try:
        audio = record_utterance(np, sounddevice)
        if audio is None:
            print("Keine Sprache erkannt.", file=sys.stderr)
            return 2
        model = WhisperModel(
            sys.argv[1], device="cpu", compute_type="int8", cpu_threads=4
        )
        segments, _ = model.transcribe(
            audio,
            language="de",
            task="transcribe",
            beam_size=5,
            temperature=0.0,
            condition_on_previous_text=False,
            vad_filter=True,
        )
        transcript = " ".join(
            segment.text.strip() for segment in segments if segment.text.strip()
        ).strip()
    except (OSError, RuntimeError, ValueError, sounddevice.PortAudioError) as error:
        print(f"Lokale Whisper-Erkennung fehlgeschlagen: {error}", file=sys.stderr)
        return 1

    if not transcript:
        print("Keine Sprache erkannt.", file=sys.stderr)
        return 2
    print(transcript, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
