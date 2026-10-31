import io

import pytest
from PIL import Image

from superscreen.capture import encode_jpeg


def test_jpeg_capture_resizes_and_is_decodable():
    image = Image.new("RGB", (1920, 1080), (32, 64, 96))
    content = encode_jpeg(image, max_width=960, quality=65)
    with Image.open(io.BytesIO(content)) as decoded:
        assert decoded.format == "JPEG"
        assert decoded.size == (960, 540)
    assert content.startswith(b"\xff\xd8")


@pytest.mark.parametrize("width,quality", [(0, 60), (4096, 60), (960, 0), (960, 100)])
def test_invalid_encoding_settings(width, quality):
    with pytest.raises(ValueError):
        encode_jpeg(Image.new("RGB", (300, 150)), width, quality)


def test_small_image_not_upscaled():
    data = encode_jpeg(Image.new("RGB", (320, 180)), max_width=960)
    with Image.open(io.BytesIO(data)) as image:
        assert image.size == (320, 180)
