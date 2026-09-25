import unittest

from app.data.disease_loader import load_diseases
from app.ui.info_screen import get_supported_disease_names


class InfoScreenDataTests(unittest.TestCase):
    def test_information_page_lists_every_supported_disease_once(self):
        names = get_supported_disease_names()
        self.assertEqual(names, [disease["name"] for disease in load_diseases()])
        self.assertEqual(len(names), 30)
        self.assertEqual(len(set(names)), 30)


if __name__ == "__main__":
    unittest.main()
