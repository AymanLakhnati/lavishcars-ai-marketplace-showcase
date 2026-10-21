"""Render a narrated evidence walkthrough. Never fabricates application interaction."""
import json
import subprocess
import textwrap
import wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output/showcase"
FRAMES = OUT / "frames"
CLIPS = OUT / "clips"
CAPTIONS = OUT / "captions"
for path in (FRAMES, CLIPS, CAPTIONS):
    path.mkdir(parents=True, exist_ok=True)
SCENES = json.loads((ROOT / "showcase/storyboard.json").read_text(encoding="utf-8"))
DATA = json.loads((OUT / "evidence.json").read_text(encoding="utf-8"))
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
W, H = 1920, 1080
BG, PANEL, INK, MUTED, GOLD, LINE = "#10231d", "#1b3229", "#f3f0e6", "#bec6b8", "#c3ac7c", "#385044"
FONTDIR = Path("C:/Windows/Fonts")


def font(size, style="regular"):
    return ImageFont.truetype(str(FONTDIR / {"regular": "segoeui.ttf", "bold": "seguisb.ttf", "serif": "georgia.ttf", "mono": "consola.ttf"}[style]), size)


def text(draw, value, xy, size=30, color=INK, width=None, style="regular", spacing=10):
    f = font(size, style)
    words = str(value).split()
    lines, current = [], ""
    for word in words:
        candidate = (current + " " + word).strip()
        if width and draw.textlength(candidate, font=f) > width and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    lines.append(current)
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=f, fill=color)
        y += size + spacing
    return y


def base(index, badge="API EVIDENCE / LOCAL DEMO"):
    scene = SCENES[index]
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    text(d, scene["kicker"], (74, 40), 19, GOLD, style="bold")
    text(d, scene["title"], (70, 80), 48, INK, width=1550, style="serif")
    d.line((74, 156, 1846, 156), fill=LINE, width=2)
    text(d, badge, (74, 174), 17, MUTED)
    for n in range(8):
        x = 74 + n * 223
        d.rounded_rectangle((x, 872, x + 204, 877), radius=2, fill=GOLD if n == index else LINE)
    text(d, f"{index + 1:02d} / 08", (74, 1040), 17, GOLD)
    text(d, "UNOFFICIAL CONCEPT  •  SYNTHETIC INVENTORY  •  SYNTHETIC NARRATION", (530, 1040), 17, MUTED)
    return im, d


def box(d, bounds, fill=PANEL):
    d.rounded_rectangle(bounds, radius=18, fill=fill, outline=LINE, width=2)


def screenshot(im, path, y=0, height=None, bounds=(74, 220, 1846, 840)):
    source = Image.open(path).convert("RGB")
    x1, y1, x2, y2 = bounds
    crop_height = height or int(source.width * (y2 - y1) / (x2 - x1))
    y = min(y, max(0, source.height - crop_height))
    source = source.crop((0, y, source.width, min(source.height, y + crop_height)))
    factor = min((x2 - x1) / source.width, (y2 - y1) / source.height)
    source = source.resize((round(source.width * factor), round(source.height * factor)), Image.Resampling.LANCZOS)
    im.paste(source, (x1 + ((x2 - x1) - source.width) // 2, y1 + ((y2 - y1) - source.height) // 2))


def bullets(d, items, x=110, y=290, width=1560, size=33):
    for item in items:
        d.ellipse((x, y + 14, x + 10, y + 24), fill=GOLD)
        y = text(d, item, (x + 32, y), size, width=width - 32) + 28


def metric(d, x, y, label, value, width=540):
    box(d, (x, y, x + width, y + 182))
    text(d, label, (x + 28, y + 24), 23, MUTED, width=width - 56)
    text(d, value, (x + 28, y + 70), 52, GOLD, width=width - 56, style="bold")


def arrow(d, start, end):
    d.line((*start, *end), fill=GOLD, width=4)
    x, y = end
    d.polygon([(x, y), (x - 14, y - 8), (x - 14, y + 8)], fill=GOLD)


def build_shots(index):
    shots = []
    def add(im):
        path = FRAMES / f"{SCENES[index]['id']}-{len(shots) + 1}.png"
        im.save(path)
        shots.append(path)
    if index == 0:
        im, d = base(index, "VERIFIED PROTOTYPE CAPTURE / EDITED WALKTHROUGH")
        screenshot(im, ROOT / "docs/screenshots/home-desktop.png", y=88)
        add(im)
        im, d = base(index, "THE BUSINESS OBJECTIVE")
        text(d, "Supplier → Approval → Discovery → Inquiry", (110, 280), 55, GOLD, width=1650, style="serif")
        bullets(d, ["A real Type A listings workflow", "Database-grounded discovery and reviewable assistance", "Prepared by Ayman Lakhnati after the technical assessment"], y=430)
        add(im)
    elif index == 1:
        im, d = base(index, "VERIFIED PROTOTYPE CAPTURE / RECORDED FIXTURE STATE")
        screenshot(im, ROOT / "docs/screenshots/concierge-desktop.png", y=480)
        add(im)
        im, d = base(index, "FRESH CONCIERGE API RESPONSE / APPROVED DATABASE OFFERS")
        for n, recommendation in enumerate(DATA["concierge"]["recommendations"]):
            listing = recommendation["listing"]
            x = 74 + n * 600
            box(d, (x, 250, x + 572, 795))
            text(d, f"OFFER #{listing['id']}  /  {listing['city'].upper()}", (x + 30, 280), 20, GOLD)
            text(d, listing["title"], (x + 30, 340), 38, width=510, style="serif")
            text(d, f"AED {listing['daily_price']:,.0f} / day", (x + 30, 480), 38, GOLD, style="bold")
            text(d, f"{listing['seats']} seats  •  {listing['category']}", (x + 30, 550), 26)
            text(d, "Eligible catalog record. Below the requested daily budget. Open the record to request a quote.", (x + 30, 620), 25, MUTED, width=505)
        add(im)
        im, d = base(index, "HOW THE CONCIERGE STAYS GROUNDED")
        bullets(d, ["Extract supported constraints; clarify a missing destination", "Apply the same eligibility rules as the public catalog", "Return database facts and explain recognized matches", "No-key rules work; a live external-model call is unverified"], y=260)
        add(im)
    elif index == 2:
        im, d = base(index)
        metric(d, 74, 245, "Preferred-category match", "+20 points")
        metric(d, 670, 245, "Editorial occasion fit", "+10 points")
        metric(d, 1266, 245, "Tie breaker", "Price, then ID", 580)
        bullets(d, ["Hard constraints stay mandatory", "Actual category and feature values come from stored offers", "Scores are transparent rules, not confidence percentages"], y=510, size=32)
        add(im)
        im, d = base(index, "FRESH INQUIRY EVIDENCE / SYNTHETIC CUSTOMER")
        workflow = DATA["workflow"]
        metric(d, 74, 245, "New synthetic offer", f"#{workflow['listing_id']}")
        metric(d, 670, 245, "Persisted inquiry", f"#{workflow['saved_inquiry_id']}")
        metric(d, 1266, 245, "Supplier inbox", "Verified", 580)
        bullets(d, ["The server derives supplier and location from the listing", "Inquiry and outbox commit before any delivery attempt", "No real supplier message, payment or confirmed booking"], y=520, size=31)
        add(im)
    elif index == 3:
        im, d = base(index, "VERIFIED SUPPLIER WORKSPACE CAPTURE / RECORDED FIXTURE STATE")
        screenshot(im, ROOT / "docs/screenshots/supplier-desktop.png", y=130)
        add(im)
        im, d = base(index, "FRESH LISTING-ASSISTANT API RESPONSE / REVIEWABLE SUGGESTIONS")
        values = DATA["assistant"]["suggestions"]
        fields = [("Vehicle", f"{values['year']} {values['brand']} {values['model']}"), ("Location / currency", f"{values['city']} / {values['currency']}"), ("Daily rate", str(values['daily_price'])), ("Passengers / transmission", f"{values['seats']} / {values['transmission']}"), ("Explicit feature", ", ".join(values['features'])), ("Authority", "Review → Apply → Save → Submit")]
        for n, (label, value) in enumerate(fields):
            x, y = 74 + (n % 2) * 900, 245 + (n // 2) * 190
            box(d, (x, y, x + 872, y + 166))
            text(d, label.upper(), (x + 28, y + 24), 19, GOLD)
            text(d, value, (x + 28, y + 67), 31, width=816)
        add(im)
        im, d = base(index, "ASSISTANCE DOES NOT BYPASS THE WORKFLOW")
        bullets(d, ["Explicitly supplied facts become editable suggestions", "Unknown specifications are not inferred from brand or photos", "Applying suggestions does not save or publish", "Authentication scopes private offers and inquiries to the supplier"], y=260)
        add(im)
    elif index == 4:
        im, d = base(index, "VERIFIED ADMIN CAPTURE / RECORDED FIXTURE STATE")
        screenshot(im, ROOT / "docs/screenshots/admin-desktop.png", y=100)
        add(im)
        im, d = base(index, "FRESH END-TO-END API CHECK / SAME NEW OFFER")
        states = [("Draft", "Saved privately"), ("Pending", "Public detail: 404"), ("Published", "Admin-approved: 200"), ("Inquiry", f"Saved #{DATA['workflow']['saved_inquiry_id']}")]
        for n, (label, value) in enumerate(states):
            x = 74 + n * 450
            box(d, (x, 310, x + 420, 580))
            text(d, f"0{n + 1}", (x + 30, 340), 28, GOLD)
            text(d, label, (x + 30, 405), 37, style="serif")
            text(d, value, (x + 30, 485), 25, MUTED, width=360)
            if n < 3:
                arrow(d, (x + 423, 445), (x + 448, 445))
        text(d, "Suspension, administrative hiding and material edits are enforced by backend rules.", (110, 665), 34, MUTED, width=1640)
        add(im)
    elif index == 5:
        im, d = base(index, "FRESH SUPPLIER-SCOPED DATABASE AGGREGATES")
        insights = DATA["insights"]
        metric(d, 74, 240, "Listing records", str(insights["totals"]["listings"]))
        metric(d, 670, 240, "Recorded inquiries", str(insights["totals"]["leads"]))
        metric(d, 1266, 240, "Scope / mode", "Supplier / factual", 580)
        text(d, "Categories attracting recorded inquiries", (100, 470), 31, GOLD)
        counts = insights["leads_by_category"]
        max_count = max(counts.values(), default=1)
        for n, (category, count) in enumerate(sorted(counts.items(), key=lambda p: -p[1])[:3]):
            y = 540 + n * 87
            text(d, category, (100, y), 27)
            d.rounded_rectangle((390, y + 5, 390 + max(6, int(1150 * count / max_count)), y + 35), radius=6, fill=GOLD)
            text(d, count, (1630, y), 29, GOLD)
        add(im)
        im, d = base(index, "FRESH PHOTO-QUALITY API CHECK / SYNTHETIC DARK TEST PATTERN")
        quality = DATA["photo_quality"]["first"]
        metric(d, 74, 245, "Resolution", f"{quality['width']} × {quality['height']}")
        metric(d, 670, 245, "Brightness (0–255)", str(quality["brightness"]))
        metric(d, 1266, 245, "Repeated upload", "Duplicate flagged", 580)
        bullets(d, ["Low resolution and excessive darkness were flagged", "Cover score combines resolution, brightness and edge detail", "No semantic vehicle detection, ownership or specification verification"], y=510, size=31)
        add(im)
        im, d = base(index, "MEASUREMENTS WITH HONEST LIMITS")
        bullets(d, ["Views count detail API calls, including repeated and automated calls", "Inquiry ratios are descriptive, not unique-customer attribution", "Summaries use actual scoped aggregates", "No invented revenue, demand forecast or prediction accuracy"], y=270)
        add(im)
    elif index == 6:
        im, d = base(index, "REAL LOCAL WORDPRESS CAPTURE / API-CONSUMING CATALOG")
        screenshot(im, OUT / "wordpress-catalog.png", height=Image.open(OUT / "wordpress-catalog.png").height)
        add(im)
        im, d = base(index, "THEME-INDEPENDENT MARKETPLACE AUTHORITY")
        nodes = [(74, "WordPress", "Content / marketing / SEO"), (674, "FastAPI", "Permissions / approval / AI"), (1274, "PostgreSQL", "Authoritative records")]
        for x, title, detail in nodes:
            box(d, (x, 300, x + 572, 580))
            text(d, title, (x + 32, 360), 43, GOLD, style="serif")
            text(d, detail, (x + 32, 460), 27, width=510)
            if x < 1274:
                arrow(d, (x + 575, 435), (x + 598, 435))
        text(d, "Next.js demonstrates the storefront and dedicated supplier/admin portals.", (110, 665), 34, MUTED, width=1650)
        add(im)
        im, d = base(index, "EXECUTED LOCAL VERIFICATION / PRECISE DELIVERY BOUNDARIES")
        metric(d, 74, 240, "Backend tests", "22 passed")
        metric(d, 670, 240, "Browser scenarios", "4 + 7 checks")
        metric(d, 1266, 240, "Proxy contracts", "5 passed", 580)
        bullets(d, ["Production build, lint and local WordPress checks passed", "Remote CI has a startup failure before jobs", "Public deployment and a real external-model call remain unverified"], y=520, size=31)
        add(im)
    else:
        im, d = base(index, "SOURCE CODE + TESTS + TECHNICAL DOCUMENTATION INCLUDED")
        text(d, "A practical foundation for the next conversation.", (110, 280), 62, GOLD, width=1610, style="serif")
        bullets(d, ["Inspect the code and reproduce the workflow", "Discuss publication, ownership and AI safeguards", "Agree the smallest production scope and WordPress rollout"], y=470, size=32)
        add(im)
        im, d = base(index, "THANK YOU FOR REVIEWING")
        text(d, "AYMAN LAKHNATI", (110, 295), 61, GOLD, style="bold")
        text(d, "LavishCars AI Marketplace", (110, 400), 52, style="serif")
        text(d, "Independent concept • AI-assisted development", (110, 505), 32, MUTED)
        text(d, "Narrated evidence walkthrough • No confirmed bookings", (110, 565), 31, MUTED)
        text(d, "Code, tests, setup instructions and requirement audit accompany this video.", (110, 700), 30, width=1620)
        add(im)
    return shots


def stamp(seconds, separator=","):
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3600000)
    minutes, milliseconds = divmod(milliseconds, 60000)
    seconds, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02}{separator}{milliseconds:03}"


def caption_blocks(value):
    words = value.replace("S U V", "SUV").replace("A P I", "API").replace("C R M", "CRM").replace("S E O", "SEO").split()
    chunks, chunk = [], []
    for word in words:
        if len(" ".join(chunk + [word])) > 100 and chunk:
            chunks.append(" ".join(chunk))
            chunk = []
        chunk.append(word)
    if chunk:
        chunks.append(" ".join(chunk))
    return chunks


def run(command, log):
    with log.open("w", encoding="utf-8") as stream:
        subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, check=True)


def main():
    manifest, all_subtitles, transcript = [], [], []
    global_time = 0.0
    for index, scene in enumerate(SCENES):
        audio = OUT / "audio" / (scene["id"] + ".wav")
        with wave.open(str(audio)) as reader:
            voice_duration = reader.getnframes() / reader.getframerate()
        duration = voice_duration + 1.2
        shots = build_shots(index)
        shot_list = OUT / (scene["id"] + ".ffconcat")
        lines = ["ffconcat version 1.0"]
        weights = {0: [.5, .5], 1: [.25, .5, .25], 2: [.66, .34], 3: [.15, .5, .35], 4: [.3, .7], 5: [.52, .33, .15], 6: [.22, .36, .42], 7: [.5, .5]}[index]
        for shot, weight in zip(shots, weights):
            lines += [f"file '{shot.relative_to(OUT).as_posix()}'", f"duration {duration * weight:.6f}"]
        lines.append(f"file '{shots[-1].relative_to(OUT).as_posix()}'")
        shot_list.write_text("\n".join(lines), encoding="utf-8")
        chunks = caption_blocks(scene["narration"])
        total_weight = sum(len(chunk.split()) for chunk in chunks)
        current, subtitles = 0.5, []
        for number, chunk in enumerate(chunks, 1):
            end = current + voice_duration * len(chunk.split()) / total_weight
            subtitles.append(f"{number}\n{stamp(current)} --> {stamp(end)}\n{textwrap.fill(chunk, width=57)}\n")
            all_subtitles.append((global_time + current, global_time + end, chunk))
            current = end
        caption = CAPTIONS / (scene["id"] + ".srt")
        caption.write_text("\n".join(subtitles), encoding="utf-8")
        clip = CLIPS / (scene["id"] + ".mp4")
        caption_path = caption.relative_to(ROOT).as_posix()
        filters = f"fps=24,zoompan=z='min(1+0.000025*on,1.025)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1920x1080:fps=24,subtitles='{caption_path}':force_style='FontName=Segoe UI,FontSize=10,PrimaryColour=&H00E6F0F3,OutlineColour=&H001D2310,BorderStyle=3,Outline=1,Shadow=0,MarginV=20',fade=t=in:st=0:d=0.25,fade=t=out:st={duration - .25:.4f}:d=0.25,format=yuv420p"
        command = [FFMPEG, "-y", "-hide_banner", "-f", "concat", "-safe", "0", "-i", str(shot_list), "-i", str(audio), "-vf", filters, "-af", f"adelay=500:all=1,apad,atrim=duration={duration:.6f},loudnorm=I=-16:TP=-1.5:LRA=11", "-t", str(duration), "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", "-threads", "4", "-c:a", "aac", "-b:a", "96k", "-ar", "48000", "-movflags", "+faststart", str(clip)]
        run(command, OUT / (scene["id"] + "-render.log"))
        manifest.append({"id": scene["id"], "title": scene["title"], "start": round(global_time, 3), "duration": round(duration, 3), "shots": [p.name for p in shots]})
        transcript.append(f"## {stamp(global_time, '.')} — {scene['title']}\n\n{scene['narration']}\n")
        global_time += duration
        print(f"Rendered {scene['id']}: {duration:.1f} seconds", flush=True)
    concat = OUT / "movie.ffconcat"
    concat.write_text("ffconcat version 1.0\n" + "\n".join(f"file 'clips/{scene['id']}.mp4'" for scene in SCENES), encoding="utf-8")
    master = OUT / "LavishCars-Ayman-Lakhnati-Demo-1080p.mp4"
    run([FFMPEG, "-y", "-hide_banner", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", "-movflags", "+faststart", str(master)], OUT / "concat.log")
    srt, vtt = [], ["WEBVTT\n"]
    for number, (start, end, chunk) in enumerate(all_subtitles, 1):
        srt.append(f"{number}\n{stamp(start)} --> {stamp(end)}\n{textwrap.fill(chunk, width=57)}\n")
        vtt.append(f"{stamp(start, '.')} --> {stamp(end, '.')}\n{chunk}\n")
    (OUT / "LavishCars-Demo.srt").write_text("\n".join(srt), encoding="utf-8")
    (OUT / "LavishCars-Demo.vtt").write_text("\n".join(vtt), encoding="utf-8")
    (OUT / "TRANSCRIPT.md").write_text("# Narrated demonstration transcript\n\nSynthetic English narration; verified captures and fresh local API evidence.\n\n" + "\n".join(transcript), encoding="utf-8")
    (OUT / "chapters.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    preview = Image.new("RGB", (1920, 1080), BG)
    for index, scene in enumerate(SCENES):
        frame = Image.open(FRAMES / f"{scene['id']}-1.png").resize((480, 270), Image.Resampling.LANCZOS)
        preview.paste(frame, ((index % 4) * 480, (index // 4) * 540))
        d = ImageDraw.Draw(preview)
        text(d, scene["title"], ((index % 4) * 480 + 18, (index // 4) * 540 + 300), 28, width=444)
    preview.save(OUT / "contact-sheet.png")
    print(f"Master complete: {global_time:.1f} seconds; {master.stat().st_size / 1048576:.1f} MB", flush=True)


if __name__ == "__main__":
    main()
