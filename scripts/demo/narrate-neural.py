"""Offline neural narration; model assets remain in ignored .runtime/tts."""
import json
from pathlib import Path
import numpy as np
import onnxruntime as rt
import soundfile as sf
from kokoro_onnx import Kokoro

ROOT = Path(__file__).resolve().parents[2]
assets = ROOT / ".runtime/tts"
options = rt.SessionOptions()
options.intra_op_num_threads = 4
session = rt.InferenceSession(str(assets / "kokoro-v1.0.onnx"), options, providers=["CPUExecutionProvider"])
voice = Kokoro.from_session(session, str(assets / "voices-v1.0.bin"))
output = ROOT / "output/showcase/audio"
output.mkdir(parents=True, exist_ok=True)
for scene in json.loads((ROOT / "showcase/storyboard.json").read_text(encoding="utf-8")):
    samples, rate = voice.create(scene["narration"].replace("LavishCars", "Lavish Cars"), voice="af_heart", speed=0.98, lang="en-us")
    assert np.isfinite(samples).all() and np.max(np.abs(samples)) > 0.05
    sf.write(output / (scene["id"] + ".wav"), samples, rate, subtype="PCM_16")
    print(f"Neural narration: {scene['id']}, {len(samples)/rate:.1f}s", flush=True)
