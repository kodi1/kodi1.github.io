import unittest
from resources.lib.data import categories
from resources.lib.dataaccess import get_categories, get_products, get_item, resolve_mpd_url


class DataAccessTests(unittest.TestCase):

    def test_get_categories_returns_the_correct_top_level_categories(self):
        """
        Verify the correct number of top categories is returned
        """
        expected_items = [c for c in categories if c.get("cat_id") is None]

        actual_items = get_categories(0)
        print("get_categories(1) returned: %s items" % len(actual_items))

        self.assertEqual(len(expected_items), len(actual_items))

    def test_get_categories_returns_the_correct_nested_categories(self):
        """
        Verified the correct number of nested category is returned
        """
        expected_items = [c for c in categories if c.get("cat_id") == 1]

        actual_items = get_categories(1)
        print("get_categories(1) returned: %s items" % len(actual_items))

        self.assertEqual(len(expected_items), len(actual_items))

    def test_get_products_returns_the_correct_number_of_products(self):
        """
        Verify the correct number of products are returned
        """
        expected_items_count = 20

        actual_items = get_products(11, 0)

        print("get_products(11, 0) returned: %s items" % len(actual_items))
        self.assertEqual(expected_items_count, len(actual_items))

    def test_get_item(self):
        item_id = 12
        expected_item = [c for c in categories if c.get("id") == item_id][0]

        actual_item = get_item(item_id)
        print("get_item returned: %s" % actual_item)

        self.assertEqual(expected_item["id"], actual_item.get("id"))
        self.assertEqual(expected_item["cat_id"], actual_item.get("cat_id"))
        self.assertEqual(expected_item.get("payload").get("main_tag_id"), actual_item.get("payload").get("main_tag_id"))
        self.assertEqual(expected_item.get("payload").get("acc_tag_id"), actual_item.get("payload").get("acc_tag_id"))

    def test_resolve_mpd_url(self):
        mpd_url = resolve_mpd_url(
            "https://gong.bg/player/bg-football/domat-na-futbola/domyt-na-futbola-28.02.2024-779757")
        print("Resolved mpd url: %s" % mpd_url)

        self.assertTrue(mpd_url.endswith(".mpd"))

    def test_full_flow(self):
        """
        Test that navigation from first top category -> first nested category -> first product -> first stream is valid
        """
        first_category_item = get_categories(0)[0]
        first_nested_category_item = get_categories(first_category_item.get("id"))[0]
        first_product = get_products(first_nested_category_item.get("id"))[0]
        mpd_url = resolve_mpd_url(first_product["url"])

        self.assertTrue(mpd_url.endswith(".mpd"))
        print("Resolved mpd url: %s" % mpd_url)


if __name__ == '__main__':
    unittest.main()
