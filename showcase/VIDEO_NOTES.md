# Video provenance and verification

The narrated demonstration is 5 minutes 29 seconds, 1920×1080, H.264/AAC, with burned-in English captions and a separate WebVTT track/transcript. English speech is generated locally with the installed Microsoft Zira voice. No voice cloning or third-party speech service is used.

This is an edited evidence walkthrough. Historical prototype screenshots are labeled **verified prototype capture / recorded fixture state**. Fresh API-response graphics are labeled separately and use the values captured by `scripts/demo/verify-evidence.py`. They are explanatory graphics, not simulated application interactions. The WordPress image was captured from a real local installation. This is not a continuous live recording or evidence of a hosted marketplace.

All five assistance areas are covered: concierge, explicit preferences, supplier suggestions, descriptive insights and basic photo quality/duplicates. Deterministic behavior and the unverified live-provider boundary are stated in the narration. Photo heuristics do not semantically verify a vehicle.

The fresh evidence check creates a synthetic offer, confirms it is private before approval, approves it, saves a fictional inquiry, verifies the supplier inbox and archives the test offer afterwards. It sends no real supplier notification. The source bundle omits confidential assessment attachments, credentials, runtime state and Git history.

Reproduction on Windows:

```powershell
services/api/.venv/Scripts/python -m pip install imageio-ffmpeg
services/api/.venv/Scripts/python scripts/demo/verify-evidence.py
node scripts/demo/capture-proof.mjs
./scripts/demo/narrate.ps1
services/api/.venv/Scripts/python scripts/demo/render.py
services/api/.venv/Scripts/python scripts/demo/package.py
```

The evidence scripts require the local API/database and local WordPress. The renderer requires Pillow, the installed Windows fonts and FFmpeg from the imageio-ffmpeg package. Generated intermediates stay under ignored `output/showcase/`.
