from PIL import Image

from package_multimap255 import frame_isometric_capture


def test_isometric_framing_preserves_the_scene_and_padding():
    panel = Image.new("RGB", (300, 200), (7, 15, 22))
    panel.paste((70, 50, 12), (50, 40, 250, 160))
    frame = frame_isometric_capture(panel)
    assert frame.size == (210, 130)
    assert frame.getpixel((5, 5)) == (70, 50, 12)


def test_framing_retains_blank_or_corner_filled_captures():
    panel = Image.new("RGB", (300, 200))
    assert frame_isometric_capture(panel) is panel
    panel.putpixel((299, 199), (255, 0, 0))
    assert frame_isometric_capture(panel) is panel
