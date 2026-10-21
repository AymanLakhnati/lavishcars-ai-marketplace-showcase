"""Publish the explicitly approved sanitized showcase; keep Git credentials in memory."""

import json
import subprocess
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NAME = "lavishcars-ai-marketplace-showcase"
credential = subprocess.run(
    ["git", "credential", "fill"],
    input="protocol=https\nhost=github.com\n\n",
    text=True,
    capture_output=True,
    check=True,
)
fields = dict(
    line.split("=", 1) for line in credential.stdout.splitlines() if "=" in line
)


def api(path, data=None, method=None):
    request = urllib.request.Request(
        "https://api.github.com" + path,
        data=json.dumps(data).encode() if data is not None else None,
        method=method,
        headers={
            "Authorization": "Bearer " + fields["password"],
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "LavishCars-showcase",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


user = api("/user")
owner = user["login"]
try:
    repository = api(f"/repos/{owner}/{NAME}")
except urllib.error.HTTPError as error:
    if error.code != 404:
        raise
    repository = api(
        "/user/repos",
        {
            "name": NAME,
            "private": False,
            "auto_init": False,
            "description": "Independent AI-assisted LavishCars Type A marketplace concept: working workflows, grounded assistance, narrated demo and tests. Synthetic data.",
        },
    )
assert repository["owner"]["login"] == owner and not repository["private"]
destination = ROOT / ".runtime/public-showcase"
destination.mkdir(parents=True, exist_ok=False)
with zipfile.ZipFile(
    ROOT / "output/showcase/LavishCars-Ayman-Lakhnati-Source.zip"
) as archive:
    for name in archive.namelist():
        target = (destination / name).resolve()
        assert target.is_relative_to(destination.resolve()), "Unsafe archive path"
    archive.extractall(destination)
video = ROOT / "showcase/LavishCars-Demo.mp4"
(destination / "showcase/LavishCars-Demo.mp4").write_bytes(video.read_bytes())
readme = destination / "README.md"
text = readme.read_text(encoding="utf-8-sig")
intro = (
    "\n[![Watch the narrated walkthrough](showcase/poster.jpg)](https://raw.githubusercontent.com/"
    + owner
    + "/"
    + NAME
    + "/main/showcase/LavishCars-Demo.mp4)\n\n**[Watch/download the 1080p narrated walkthrough](https://raw.githubusercontent.com/"
    + owner
    + "/"
    + NAME
    + "/main/showcase/LavishCars-Demo.mp4)** · [Transcript](showcase/TRANSCRIPT.md) · [Review guide](REVIEW_START_HERE.md)\n"
)
text = text.replace("## Run locally", intro + "\n## Run locally")
readme.write_text(text, encoding="utf-8")
for path in destination.rglob("*.md"):
    text = path.read_text(encoding="utf-8-sig")
    text = text.replace(
        "https://github.com/AymanLakhnati/lavishcars-ai-marketplace/",
        repository["html_url"] + "/",
    )
    text = text.replace(
        "The repository is private because it includes the original confidential assessment.",
        "This is the sanitized public review distribution. Confidential assessment attachments are omitted.",
    )
    path.write_text(text, encoding="utf-8")
(
    destination / "MANIFEST.sha256"
).unlink()  # The ZIP manifest applies to its original payload, not this new repository.
assert not (destination / "docs/references").exists()
for command in (
    ["git", "init", "-b", "main"],
    ["git", "config", "user.name", "Ayman Lakhnati"],
    ["git", "config", "user.email", f"{user['id']}+{owner}@users.noreply.github.com"],
    ["git", "remote", "add", "origin", repository["clone_url"]],
    ["git", "add", "-A"],
    [
        "git",
        "commit",
        "-m",
        "Publish sanitized marketplace prototype, narrated demo and review documentation",
    ],
    ["git", "push", "-u", "origin", "main"],
):
    subprocess.run(command, cwd=destination, check=True)
metadata = {
    "url": repository["html_url"],
    "owner": owner,
    "name": NAME,
    "path": str(destination),
    "private": False,
}
(ROOT / ".runtime/public-repo.json").write_text(
    json.dumps(metadata, indent=2), encoding="utf-8"
)
print(json.dumps(metadata))
