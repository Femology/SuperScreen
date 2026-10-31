"""Small JPEG capture pipeline for Phase 1.

This mirrors an existing monitor. It does not create or drive a virtual display.
"""
from __future__ import annotations

from io import BytesIO

from PIL import Image


def encode_jpeg(image: Image.Image, max_width: int = 960, quality: int = 60) -> bytes:
    """Compress a screenshot with a bounded width for inexpensive mobile viewing."""
    if max_width < 160 or max_width > 3840:
        raise ValueError("max_width must be between 160 and 3840")
    if quality < 20 or quality > 95:
        raise ValueError("quality must be between 20 and 95")
    resized = image.convert("RGB")
    if resized.width > max_width:
        height = max(1, round(resized.height * max_width / resized.width))
        resized = resized.resize((max_width, height), Image.Resampling.BILINEAR)
    out = BytesIO()
    resized.save(out, format="JPEG", quality=quality, optimize=False)
    return out.getvalue()


def list_monitors() -> list[dict[str, int]]:
    import mss

    with mss.mss() as sct:
        return [
            {"index":idx, "left":mon["left"], "top":mon["top"],
             "width":mon["width"], "height":mon["height"]}
            for idx, mon in enumerate(sct.monitors) if idx > 0
        ]


class CaptureSession:
    """Keep one MSS handle per client. Construct inside the streaming coroutine."""

    def __enter__(self) -> "CaptureSession":
        import mss

        self._sct = mss.mss()
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        self._sct.close()

    def frame(self, monitor_index: int, max_width: int, quality: int) -> bytes:
        from PIL import Image

        if monitor_index < 1 or monitor_index >= len(self._sct.monitors):
            raise ValueError(f"Monitor {monitor_index} is not available")
        shot = self._sct.grab(self._sct.monitors[monitor_index])
        image = Image.frombytes("RGB", shot.size, shot.rgb)
        return encode_jpeg(image, max_width=max_width, quality=quality)
