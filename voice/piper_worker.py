import base64
import importlib
import json
import os
import sys
import tempfile
import time
import wave
import winsound


def main():
    model_path = sys.argv[1]
    speaker_id = int(sys.argv[2])
    config = importlib.import_module("piper.config")
    voice_module = importlib.import_module("piper.voice")
    onnxruntime = importlib.import_module("onnxruntime")
    with open(model_path + ".json", encoding="utf-8") as config_file:
        voice_config = config.PiperConfig.from_dict(json.load(config_file))
    session_options = onnxruntime.SessionOptions()
    session_options.intra_op_num_threads = 1
    session_options.inter_op_num_threads = 1
    session_options.execution_mode = onnxruntime.ExecutionMode.ORT_SEQUENTIAL
    session = onnxruntime.InferenceSession(
        model_path,
        sess_options=session_options,
        providers=["CPUExecutionProvider"],
    )
    voice = voice_module.PiperVoice(config=voice_config, session=session)
    synthesis = config.SynthesisConfig(speaker_id=speaker_id)

    with tempfile.TemporaryDirectory(prefix="nova_voice_") as temp_dir:
        current_audio = None
        current_audio_until = 0.0
        for index, line in enumerate(sys.stdin):
            text = base64.b64decode(line).decode("utf-8").strip()
            if not text:
                continue
            if current_audio is not None:
                winsound.PlaySound(None, 0)
                os.remove(current_audio)
                current_audio = None
            output_path = os.path.join(temp_dir, f"{index}.wav")
            with wave.open(output_path, "wb") as audio_file:
                voice.synthesize_wav(text, audio_file, syn_config=synthesis)
            with wave.open(output_path, "rb") as audio_file:
                duration = audio_file.getnframes() / audio_file.getframerate()
            winsound.PlaySound(output_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            current_audio = output_path
            current_audio_until = time.monotonic() + duration
        if current_audio is not None:
            time.sleep(max(0.0, current_audio_until - time.monotonic()))
            winsound.PlaySound(None, 0)


if __name__ == "__main__":
    main()
