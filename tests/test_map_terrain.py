import tempfile
import unittest
from pathlib import Path

from PIL import Image

from game.map_terrain import build_terrain_profile


class MapTerrainTest(unittest.TestCase):
    def test_walkability_profile_reads_bright_and_dark_regions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "terrain.png"
            img = Image.new("RGB", (64, 64), (18, 18, 18))
            for x in range(32, 64):
                for y in range(0, 64):
                    img.putpixel((x, y), (220, 220, 220))
            img.save(path)

            profile = build_terrain_profile(str(path), 64, 64, forced_walkable=((0, 0),))

            self.assertFalse(profile.is_walkable(0, 32))
            self.assertTrue(profile.is_walkable(32, 32))
            self.assertTrue(profile.is_walkable(0, 0))

    def test_generated_map_variants_exist(self):
        self.assertTrue((Path("assets/maps") / "streets_neon_rain.png").exists())
        self.assertTrue((Path("assets/maps") / "bridge_breach.png").exists())


if __name__ == "__main__":
    unittest.main()
