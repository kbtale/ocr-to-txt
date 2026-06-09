from pathlib import Path

from PIL import Image, ImageDraw


BASE_DIR = Path(__file__).resolve().parent
FIXTURES_DIR = BASE_DIR / "fixtures"


def draw_low_contrast(path: Path):
    image = Image.new("RGB", (400, 300), (190, 190, 190))
    draw = ImageDraw.Draw(image)
    draw.rectangle((40, 60, 360, 105), fill=(170, 170, 170))
    draw.rectangle((40, 130, 330, 175), fill=(205, 205, 205))
    draw.rectangle((40, 200, 350, 245), fill=(175, 175, 175))
    image.save(path)


def draw_two_columns(path: Path):
    image = Image.new("RGB", (1200, 800), "white")
    draw = ImageDraw.Draw(image)

    left_boxes = [
        (60, 80, 470, 145),
        (60, 185, 440, 250),
        (60, 290, 455, 355),
    ]
    right_boxes = [
        (680, 80, 1110, 145),
        (680, 185, 1080, 250),
        (680, 290, 1095, 355),
    ]

    for box in left_boxes + right_boxes:
        draw.rectangle(box, fill=(0, 0, 0))

    image.save(path)


def draw_single_block(path: Path):
    image = Image.new("RGB", (900, 500), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((100, 120, 820, 180), fill=(0, 0, 0))
    draw.rectangle((100, 230, 760, 290), fill=(0, 0, 0))
    image.save(path)


def main():
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    draw_low_contrast(FIXTURES_DIR / "low_contrast.png")
    draw_two_columns(FIXTURES_DIR / "two_columns.png")
    draw_single_block(FIXTURES_DIR / "single_block.png")


if __name__ == "__main__":
    main()
