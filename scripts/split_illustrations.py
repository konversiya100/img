from pathlib import Path
from PIL import Image, ImageOps, ImageFilter
import re

SHEETS = Path("sheets")
for source in sorted(SHEETS.glob("*.png")):
    match = re.fullmatch(r"([a-z]+)-(\d{2})", source.stem)
    if not match:
        continue
    group, part_text = match.groups()
    part = int(part_text)
    if group not in {"mtg", "aircon", "jk", "atelier"}:
        continue
    with Image.open(source) as sheet:
        sheet = sheet.convert("RGB")
        width, height = sheet.size
        out_dir = Path(group)
        out_dir.mkdir(exist_ok=True)
        for i in range(6):
            col, row = i % 2, i // 2
            left = round(col * width / 2)
            right = round((col + 1) * width / 2)
            top = round(row * height / 3)
            bottom = round((row + 1) * height / 3)
            inset = 2
            panel = sheet.crop((left + inset, top + inset, right - inset, bottom - inset))
            # 4:5 portrait, all panels rendered to an upload-friendly size
            panel = ImageOps.fit(panel, (900, 1125), method=Image.Resampling.LANCZOS)
            panel = panel.filter(ImageFilter.UnsharpMask(radius=1.3, percent=65, threshold=3))
            number = (part - 1) * 6 + i + 1
            panel.save(out_dir / f"post-{number:02d}.jpg", "JPEG", quality=89, optimize=True)
            print(f"{source}: {group}/post-{number:02d}.jpg")
