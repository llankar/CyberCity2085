import json
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "generated_token_manifest.json"
EXPECTED_CATEGORIES = {
    "mutants",
    "starvers",
    "raiders",
    "mutant_animals",
    "giant_combat_robots",
}


class GeneratedTokenAssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_manifest_has_expected_categories(self):
        categories = {category["category"] for category in self.manifest["categories"]}
        self.assertEqual(categories, EXPECTED_CATEGORIES)

    def test_each_category_has_at_least_twenty_tokens(self):
        for category in self.manifest["categories"]:
            self.assertGreaterEqual(category["count"], 20, category["category"])
            self.assertEqual(category["count"], len(category["tokens"]), category["category"])

    def test_token_files_are_rgba_and_transparent(self):
        for category in self.manifest["categories"]:
            for token in category["tokens"]:
                for field, size in (("file_512", (512, 512)), ("file_64", (64, 64))):
                    path = ROOT / token[field]
                    with self.subTest(path=path.name):
                        self.assertTrue(path.exists(), path)
                        with Image.open(path) as image:
                            self.assertEqual(image.size, size)
                            self.assertEqual(image.mode, "RGBA")
                            alpha = image.getchannel("A")
                            self.assertEqual(alpha.getextrema()[0], 0)
                            self.assertGreater(alpha.getextrema()[1], 0)
                            corners = [
                                alpha.getpixel((0, 0)),
                                alpha.getpixel((image.width - 1, 0)),
                                alpha.getpixel((0, image.height - 1)),
                                alpha.getpixel((image.width - 1, image.height - 1)),
                            ]
                            self.assertEqual(corners, [0, 0, 0, 0])


if __name__ == "__main__":
    unittest.main()
