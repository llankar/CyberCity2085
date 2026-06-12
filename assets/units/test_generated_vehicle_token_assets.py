import json
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "generated_vehicle_token_manifest.json"
EXPECTED_COUNTS = {
    "terrestrial_civilian_vehicles": 10,
    "terrestrial_military_vehicles": 10,
    "aerial_civilian_vehicles": 10,
    "aerial_military_vehicles": 10,
    "crashed_aerial_civilian_vehicles": 10,
    "crashed_aerial_military_vehicles": 10,
}


class GeneratedVehicleTokenAssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.categories = {
            category["category"]: category
            for category in cls.manifest["categories"]
        }

    def test_manifest_has_expected_categories_and_counts(self):
        self.assertEqual(set(self.categories), set(EXPECTED_COUNTS))
        for category, count in EXPECTED_COUNTS.items():
            self.assertEqual(self.categories[category]["count"], count, category)
            self.assertEqual(len(self.categories[category]["tokens"]), count, category)

    def test_aerial_tokens_include_at_least_four_vtols(self):
        aerial_tokens = (
            self.categories["aerial_civilian_vehicles"]["tokens"]
            + self.categories["aerial_military_vehicles"]["tokens"]
        )
        vtol_count = sum(1 for token in aerial_tokens if token.get("vtol"))
        self.assertGreaterEqual(vtol_count, 4)

    def test_each_aerial_token_has_matching_crashed_version(self):
        for source_name, crashed_name in (
            ("aerial_civilian_vehicles", "crashed_aerial_civilian_vehicles"),
            ("aerial_military_vehicles", "crashed_aerial_military_vehicles"),
        ):
            source_ids = {token["id"] for token in self.categories[source_name]["tokens"]}
            crashed_ids = {
                token["crashed_of_id"]
                for token in self.categories[crashed_name]["tokens"]
                if token.get("crashed")
            }
            self.assertEqual(crashed_ids, source_ids)

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
