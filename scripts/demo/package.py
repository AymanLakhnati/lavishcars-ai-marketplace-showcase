"""Create an employer source distribution without confidential attachments or runtime data."""
import hashlib
import re
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output/showcase"
OUT.mkdir(parents=True, exist_ok=True)
files = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT).decode().split("\0")
source = {}
for name in sorted(set(files)):
    path = ROOT / name
    if not path.is_file() or name.startswith(("docs/references/", "output/", ".runtime/", ".git/")):
        continue
    if path.suffix.lower() in (".mp4", ".zip", ".wav", ".webm"):
        continue
    data = path.read_bytes()
    if path.suffix.lower() in (".md", ".txt"):
        text = data.decode("utf-8-sig")
        text = re.sub(r"\[([^\]]+)\]\([^)]*references/(?:case-study|MASTER_PROMPT)[^)]*\)", r"\1 (confidential source omitted)", text)
        data = text.encode("utf-8")
    if re.search(rb"(?:gh[pousr]_[A-Za-z0-9]{30,}|sk-(?:proj-)?[A-Za-z0-9_-]{35,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)", data):
        raise RuntimeError("Potential secret in source distribution: " + name)
    source[name] = data
source["README.md"] = (ROOT / "showcase/SOURCE_README.md").read_bytes()
source["REVIEW_START_HERE.md"] = (ROOT / "showcase/REVIEW_START_HERE.md").read_bytes()
source["docs/LOCAL_SETUP.md"] = (ROOT / "README.md").read_bytes()
manifest = "\n".join(hashlib.sha256(data).hexdigest() + "  " + name for name, data in sorted(source.items())) + "\n"
source["MANIFEST.sha256"] = manifest.encode()
destination = OUT / "LavishCars-Ayman-Lakhnati-Source.zip"
with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
    for name, data in sorted(source.items()):
        archive.writestr(name, data)
with zipfile.ZipFile(destination) as archive:
    assert archive.testzip() is None
    assert "services/api/app/main.py" in archive.namelist()
    assert "apps/web/app/page.tsx" in archive.namelist()
    assert not any(name.startswith("docs/references/") for name in archive.namelist())
print(f"Employer source bundle: {len(source)} files, {destination.stat().st_size / 1048576:.2f} MB")
