from pathlib import Path
from PIL import Image, ImageDraw

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"


def _make_low_contrast_scan(path: Path) -> None:
    image = Image.new("L", (240, 120), 220)
    draw = ImageDraw.Draw(image)
    for y in (20, 42, 64, 86):
        draw.rectangle((18, y, 210, y + 10), fill=176)
    image.save(path)


def _make_two_column_page(path: Path) -> None:
    image = Image.new("L", (320, 180), 255)
    draw = ImageDraw.Draw(image)
    draw.rectangle((20, 18, 118, 44), fill=35)
    draw.rectangle((20, 68, 118, 94), fill=35)
    draw.rectangle((196, 26, 294, 52), fill=35)
    draw.rectangle((196, 78, 294, 104), fill=35)
    image.save(path)


def _make_rotated_page(path: Path) -> None:
    image = Image.new("L", (320, 180), 255)
    draw = ImageDraw.Draw(image)
    draw.rectangle((20, 18, 118, 44), fill=35)
    draw.rectangle((20, 68, 118, 94), fill=35)
    draw.rectangle((196, 26, 294, 52), fill=35)
    draw.rectangle((196, 78, 294, 104), fill=35)
    rotated = image.rotate(10, expand=True, fillcolor=255)
    rotated.save(path)


def ensure_fixtures() -> None:
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)

    low_contrast = FIXTURE_DIR / "low_contrast_scan.png"
    two_column = FIXTURE_DIR / "two_column_page.png"
    rotated = FIXTURE_DIR / "rotated_page.png"

    if not low_contrast.exists():
        _make_low_contrast_scan(low_contrast)
    if not two_column.exists():
        _make_two_column_page(two_column)
    if not rotated.exists():
        _make_rotated_page(rotated)
