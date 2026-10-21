"""Render a narrated evidence walkthrough. Never fabricates application interaction."""

import json
import subprocess
import textwrap
import wave
import numpy as np
import soundfile as sf
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
BG, PANEL, INK, MUTED, GOLD, LINE = (
    "#10231d",
    "#1b3229",
    "#f3f0e6",
    "#bec6b8",
    "#c3ac7c",
    "#385044",
)
FONTDIR = Path("C:/Windows/Fonts")


def font(size, style="regular"):
    return ImageFont.truetype(
        str(
            FONTDIR
            / {
                "regular": "segoeui.ttf",
                "bold": "seguisb.ttf",
                "serif": "georgia.ttf",
                "mono": "consola.ttf",
            }[style]
        ),
        size,
    )


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
    for n in range(len(SCENES)):
        x = 74 + n * (1772 / len(SCENES))
        d.rounded_rectangle(
            (x, 872, x + (1772 / len(SCENES)) - 18, 877), radius=2, fill=GOLD if n == index else LINE
        )
    text(d, f"{index + 1:02d} / {len(SCENES):02d}", (74, 1040), 17, GOLD)
    text(
        d,
        "UNOFFICIAL CONCEPT  •  SYNTHETIC INVENTORY  •  SYNTHETIC NARRATION",
        (530, 1040),
        17,
        MUTED,
    )
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
    source = source.resize(
        (round(source.width * factor), round(source.height * factor)),
        Image.Resampling.LANCZOS,
    )
    im.paste(
        source,
        (x1 + ((x2 - x1) - source.width) // 2, y1 + ((y2 - y1) - source.height) // 2),
    )


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
        im.save(path); shots.append(path)
    def capture(name, y=0, label="VERIFIED PROTOTYPE CAPTURE / EDITED WALKTHROUGH"):
        im, d = base(index, label)
        screenshot(im, ROOT / "docs/screenshots" / name, y=y)
        add(im)
    def cards(items, label="IMPLEMENTED FEATURES / EXPLANATORY GRAPHIC"):
        im, d = base(index, label)
        for n, (title, description) in enumerate(items):
            x = 74 + (n % 2) * 900; y = 245 + (n // 2) * 290
            box(d, (x,y,x+872,y+255))
            text(d, f"0{n+1}", (x+30,y+25), 22, GOLD)
            text(d, title, (x+30,y+75), 35, style="serif", width=810)
            text(d, description, (x+30,y+142), 26, MUTED, width=810)
        add(im)
    if index == 0:
        from PIL import ImageOps
        im = ImageOps.fit(Image.open(ROOT / "apps/web/public/images/hero-concept.webp").convert("RGB"), (W,H))
        shade = Image.new("RGBA", (W,H))
        sd = ImageDraw.Draw(shade)
        for x in range(W):
            sd.line((x,0,x,H), fill=(8,24,19,max(20,int(210*(1-x/W)))))
        im = Image.alpha_composite(im.convert("RGBA"),shade).convert("RGB"); d = ImageDraw.Draw(im)
        text(d,"LAVISHCARS",(90,80),34,GOLD,style="bold")
        text(d,"Every journey\ndeserves an entrance.",(90,235),76,INK,style="serif",width=1100,spacing=18)
        text(d,"A marketplace concept by Ayman Lakhnati",(95,475),29)
        text(d,"DISCOVER  /  SUPPLY  /  CONNECT",(95,550),22,GOLD)
        text(d,"INDEPENDENT CONCEPT  •  AI-GENERATED ARTWORK  •  SYNTHETIC NARRATION",(95,1040),17)
        add(im)
        capture("home-desktop.png", y=0)
    elif index == 1:
        capture("home-desktop.png",y=1030)
        im,d=base(index,"VERIFIED MOBILE CAPTURE / RESPONSIVE DISCOVERY")
        screenshot(im,ROOT/"docs/screenshots/fleet-mobile.png",height=1400,bounds=(90,220,620,840))
        text(d,"Your priorities.\nYour shortlist.",(730,285),53,GOLD,style="serif",width=1030)
        bullets(d,["Destination, category and budget","Passenger, transmission and feature filters","Daily, weekly and monthly rates","Vehicle details → structured quote request"],x=740,y=465,width=1000,size=29)
        add(im)
    elif index == 2:
        capture("supplier-desktop.png",y=380)
        cards([("Fleet lifecycle","Draft → submit → review → published. Pause and archive when needed."),("Offer editor","Specifications, rental periods, features and ordered photos."),("Profile & team","Supplier account details, owner/member roles and service areas."),("Inquiry inbox","Supplier-scoped requests with controlled status updates.")])
    elif index == 3:
        capture("admin-desktop.png",y=310)
        cards([("Supplier governance","Approve, reject or suspend; preserve business history."),("Listing moderation","Publish, reject with a reason or administratively hide."),("Catalog management","Brands, models and categories, separate from the theme."),("Location hierarchy","Country, state, city, area and airport controls; cycles rejected.")])
    elif index == 4:
        im,d=base(index,"VERIFIED API WORKFLOW / EXPLANATORY GRAPHIC")
        stages=[("Draft","Saved privately"),("Pending","Public detail: 404"),("Approved","Public detail: 200"),("Inquiry",f"Saved #{DATA['workflow']['saved_inquiry_id']}")]
        for n,(title,detail) in enumerate(stages):
            x=74+n*450;box(d,(x,300,x+420,590));text(d,f"0{n+1}",(x+30,335),26,GOLD)
            text(d,title,(x+30,410),38,style="serif");text(d,detail,(x+30,490),26,MUTED,width=360)
            if n<3:arrow(d,(x+422,445),(x+448,445))
        text(d,"One offer. The same publication boundary. A persisted supplier inquiry.",(100,680),32,GOLD,width=1720)
        add(im)
        im,d=base(index,"REAL LOCAL WORDPRESS CAPTURE / API-CONSUMING CATALOG")
        screenshot(im,OUT/"wordpress-catalog.png",height=669,bounds=(74,220,940,840))
        text(d,"Keep the content.\nConnect the catalog.",(1010,300),47,GOLD,style="serif",width=780)
        text(d,"WordPress bridge consumes eligible offers from the marketplace API.",(1015,500),30,width=770)
        text(d,"Local integration verified; production rollout remains a next step.",(1015,660),26,MUTED,width=770)
        add(im)
    elif index == 5:
        capture("concierge-desktop.png",y=130)
        im,d=base(index,"VERIFIED CONCIERGE RESPONSE / DATABASE OFFER FACTS")
        text(d,'“Dubai. Four days. A luxury SUV. Below AED 1,000 a day.”',(95,245),35,GOLD,width=1710,style="serif")
        for n,recommendation in enumerate(DATA["concierge"]["recommendations"]):
            listing=recommendation["listing"];x=74+n*600
            box(d,(x,340,x+572,805))
            text(d,listing["title"],(x+30,375),36,width=510,style="serif")
            text(d,f"AED {listing['daily_price']:,.0f} / day",(x+30,510),37,GOLD,style="bold")
            text(d,f"{listing['city']}  •  {listing['seats']} seats",(x+30,585),26)
            text(d,"Approved offer. Fits the requested daily budget. Open the record to inquire.",(x+30,655),25,MUTED,width=510)
        add(im)
    elif index == 6:
        cards([("Mandatory constraints","Destination, budget, passengers and required features remain mandatory."),("Explainable ranking","Category match +20. Occasion fit +10. Ties use price, then ID."),("Editable suggestions","Explicit rough notes become proposed fields and completeness warnings."),("Human review","Preview → apply → edit → save → submit. No automatic publication.")],"VERIFIED AI SERVICE BEHAVIOR / EXPLANATORY GRAPHIC")
        im,d=base(index,"VERIFIED LISTING-ASSISTANT RESPONSE / EXPLANATORY GRAPHIC")
        values=DATA["assistant"]["suggestions"]
        text(d,"Rough notes → a reviewable draft",(100,255),49,GOLD,width=1710,style="serif")
        details=[("Vehicle",f"{values['year']} {values['brand']} {values['model']}"),("Destination",f"{values['city']} / {values['currency']}"),("Daily rate",str(values['daily_price'])),("Review boundary","Apply does not save or publish")]
        for n,(title,detail) in enumerate(details):
            x=74+(n%2)*900;y=370+(n//2)*205;box(d,(x,y,x+872,y+175))
            text(d,title.upper(),(x+30,y+25),20,GOLD);text(d,detail,(x+30,y+78),32,width=810)
        add(im)
    elif index == 7:
        im,d=base(index,"VERIFIED SUPPLIER-SCOPED AGGREGATES / EXPLANATORY GRAPHIC")
        insights=DATA["insights"]
        metric(d,74,240,"Listing records",str(insights["totals"]["listings"]))
        metric(d,670,240,"Recorded inquiries",str(insights["totals"]["leads"]))
        metric(d,1266,240,"Scope","Supplier",580)
        text(d,"Categories attracting recorded inquiries",(100,475),32,GOLD)
        counts=insights["leads_by_category"];peak=max(counts.values(),default=1)
        for n,(category,count) in enumerate(sorted(counts.items(),key=lambda p:-p[1])[:3]):
            y=550+n*85;text(d,category,(100,y),27);d.rounded_rectangle((390,y+5,390+max(6,int(1130*count/peak)),y+34),radius=6,fill=GOLD);text(d,count,(1630,y),29,GOLD)
        add(im)
        cards([("Photo quality","Resolution, brightness and edge detail flag weak uploads."),("Duplicate detection","Identical normalized uploads are flagged for review."),("Cover candidates","A documented quality score supports image ordering."),("Precise boundaries","No vehicle identity or ownership verification. Views include repeat API calls.")],"VERIFIED LOCAL IMAGE HEURISTICS / EXPLANATORY GRAPHIC")
    else:
        im,d=base(index,"EXECUTED LOCAL CHECKS / SOURCE AND ROADMAP AVAILABLE")
        metric(d,74,240,"Backend tests","22 passed");metric(d,670,240,"Browser verification","4 + 7 checks");metric(d,1266,240,"Proxy contracts","5 passed",580)
        text(d,"Next.js  /  FastAPI  /  PostgreSQL  /  WordPress bridge",(100,500),38,GOLD,width=1720,style="serif")
        text(d,"Public review page + source code + reproducible setup + production roadmap",(100,610),32,width=1720)
        text(d,"Full application hosting and a live external-model call remain unverified.",(100,735),26,MUTED,width=1720)
        add(im)
        im,d=base(index,"PREPARED AFTER THE LAVISHCARS TECHNICAL ASSESSMENT")
        text(d,"AYMAN LAKHNATI",(110,280),63,GOLD,style="bold")
        text(d,"Product thinking. Working evidence.",(110,405),59,style="serif",width=1680)
        text(d,"Let’s discuss the decisions behind the experience.",(115,560),35,MUTED,width=1640)
        text(d,"Independent concept • AI-assisted development • Synthetic inventory",(115,720),27,GOLD,width=1640)
        add(im)
    return shots


def stamp(seconds, separator=","):
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3600000)
    minutes, milliseconds = divmod(milliseconds, 60000)
    seconds, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02}{separator}{milliseconds:03}"


def caption_blocks(value):
    words = (
        value.replace("S U V", "SUV")
        .replace("A P I", "API")
        .replace("C R M", "CRM")
        .replace("S E O", "SEO")
        .split()
    )
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
        subprocess.run(
            command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, check=True
        )


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
        weights = [0.4, 0.6] if index in (0, 5) else [0.55, 0.45]
        for shot, weight in zip(shots, weights):
            lines += [
                f"file '{shot.relative_to(OUT).as_posix()}'",
                f"duration {duration * weight:.6f}",
            ]
        lines.append(f"file '{shots[-1].relative_to(OUT).as_posix()}'")
        shot_list.write_text("\n".join(lines), encoding="utf-8")
        chunks = caption_blocks(scene["narration"])
        total_weight = sum(len(chunk.split()) for chunk in chunks)
        current, subtitles = 0.5, []
        for number, chunk in enumerate(chunks, 1):
            end = current + voice_duration * len(chunk.split()) / total_weight
            subtitles.append(
                f"{number}\n{stamp(current)} --> {stamp(end)}\n{textwrap.fill(chunk, width=57)}\n"
            )
            all_subtitles.append((global_time + current, global_time + end, chunk))
            current = end
        caption = CAPTIONS / (scene["id"] + ".srt")
        caption.write_text("\n".join(subtitles), encoding="utf-8")
        clip = CLIPS / (scene["id"] + ".mp4")
        caption_path = caption.relative_to(ROOT).as_posix()
        filters = f"fps=24,zoompan=z='min(1+0.000015*on,1.015)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1920x1080:fps=24,subtitles='{caption_path}':force_style='FontName=Segoe UI,FontSize=10,PrimaryColour=&H00E6F0F3,OutlineColour=&H001D2310,BorderStyle=3,Outline=1,Shadow=0,MarginV=20',fade=t=in:st=0:d=0.25,fade=t=out:st={duration - 0.25:.4f}:d=0.25,format=yuv420p"
        command = [
            FFMPEG,
            "-y",
            "-hide_banner",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(shot_list),
            "-i",
            str(audio),
            "-vf",
            filters,
            "-af",
            f"adelay=500:all=1,apad,atrim=duration={duration:.6f},loudnorm=I=-16:TP=-1.5:LRA=11",
            "-t",
            str(duration),
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "24",
            "-threads",
            "4",
            "-c:a",
            "aac",
            "-b:a",
            "96k",
            "-ar",
            "48000",
            "-movflags",
            "+faststart",
            str(clip),
        ]
        run(command, OUT / (scene["id"] + "-render.log"))
        manifest.append(
            {
                "id": scene["id"],
                "title": scene["title"],
                "start": round(global_time, 3),
                "duration": round(duration, 3),
                "shots": [p.name for p in shots],
            }
        )
        transcript.append(
            f"## {stamp(global_time, '.')} — {scene['title']}\n\n{scene['narration']}\n"
        )
        global_time += duration
        print(f"Rendered {scene['id']}: {duration:.1f} seconds", flush=True)
    concat = OUT / "movie.ffconcat"
    concat.write_text(
        "ffconcat version 1.0\n"
        + "\n".join(f"file 'clips/{scene['id']}.mp4'" for scene in SCENES),
        encoding="utf-8",
    )
    picture = OUT / "picture-with-voice.mp4"
    run(
        [
            FFMPEG,
            "-y",
            "-hide_banner",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat),
            "-c",
            "copy",
            "-movflags",
            "+faststart",
            str(picture),
        ],
        OUT / "concat.log",
    )
    # Original, quiet synthesized score. No recordings, samples or licensed songs.
    rate = 24000
    samples = np.arange(round(global_time * rate), dtype=np.float32) / rate
    bed = np.zeros_like(samples)
    bar = 60 / 88 * 4
    chords = [(146.83, 174.61, 220), (116.54, 146.83, 174.61),
              (130.81, 174.61, 220), (130.81, 164.81, 196)]
    for n in range(int(global_time / (bar * 2)) + 1):
        start = n * bar * 2
        local = samples - start
        mask = (local >= 0) & (local < bar * 2)
        phase = local[mask]
        envelope = np.minimum(phase / 0.6, 1) * np.minimum((bar * 2 - phase) / 0.8, 1)
        for frequency in chords[n % 4]:
            bed[mask] += 0.075 * envelope * np.sin(2 * np.pi * frequency * phase)
        for beat in range(8):
            t = phase - beat * bar / 4
            pulse = (t >= 0) * np.exp(-np.maximum(t, 0) * 9)
            bed[mask] += 0.03 * pulse * np.sin(2 * np.pi * chords[n % 4][2] * 2 * phase)
    bed *= np.minimum(samples / 2, 1) * np.minimum((global_time - samples) / 3, 1)
    music = OUT / "original-score.wav"
    sf.write(music, bed, rate, subtype="PCM_16")
    master = OUT / "LavishCars-Ayman-Lakhnati-Demo-1080p.mp4"
    run([FFMPEG, "-y", "-hide_banner", "-i", str(picture), "-i", str(music),
         "-filter_complex", "[1:a]volume=0.09[bed];[0:a][bed]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95:level=0[a]",
         "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
         "-movflags", "+faststart", str(master)], OUT / "sound-mix.log")
    srt, vtt = [], ["WEBVTT\n"]
    for number, (start, end, chunk) in enumerate(all_subtitles, 1):
        srt.append(
            f"{number}\n{stamp(start)} --> {stamp(end)}\n{textwrap.fill(chunk, width=57)}\n"
        )
        vtt.append(f"{stamp(start, '.')} --> {stamp(end, '.')}\n{chunk}\n")
    (OUT / "LavishCars-Demo.srt").write_text("\n".join(srt), encoding="utf-8")
    (OUT / "LavishCars-Demo.vtt").write_text("\n".join(vtt), encoding="utf-8")
    (OUT / "TRANSCRIPT.md").write_text(
        "# Narrated demonstration transcript\n\nSynthetic English narration; verified captures and fresh local API evidence.\n\n"
        + "\n".join(transcript),
        encoding="utf-8",
    )
    (OUT / "chapters.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    preview = Image.new("RGB", (1920, 1440), BG)
    for index, scene in enumerate(SCENES):
        frame = Image.open(FRAMES / f"{scene['id']}-1.png").resize(
            (640, 360), Image.Resampling.LANCZOS
        )
        preview.paste(frame, ((index % 3) * 640, (index // 3) * 480))
        d = ImageDraw.Draw(preview)
        text(
            d,
            scene["title"],
            ((index % 3) * 640 + 18, (index // 3) * 480 + 375),
            28,
            width=604,
        )
    preview.save(OUT / "contact-sheet.png")
    print(
        f"Master complete: {global_time:.1f} seconds; {master.stat().st_size / 1048576:.1f} MB",
        flush=True,
    )


if __name__ == "__main__":
    main()
