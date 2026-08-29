from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(ALLOWED_HOSTS=['testserver'])
class BuyerDashboardViewsTests(TestCase):
    def test_buyer_listing_page_loads(self):
        response = self.client.get(reverse('dashboard:buyer'))
        self.assertEqual(response.status_code, 200)

    def test_buyer_detail_page_loads(self):
        response = self.client.get(reverse('dashboard:buyer_detail', args=['engineering-mechanics-textbook']))
        self.assertEqual(response.status_code, 200)

    def test_buyer_search_and_category_filter_routes(self):
        response = self.client.get(reverse('dashboard:buyer') + '?q=calculator')
        self.assertEqual(response.status_code, 200)

        category_response = self.client.get(reverse('dashboard:buyer') + '?category=textbooks')
        self.assertEqual(category_response.status_code, 200)

    def test_buyer_cart_page_loads(self):
        response = self.client.get(reverse('dashboard:buyer_cart'))
        self.assertEqual(response.status_code, 200)

    def test_buyer_detail_has_multiple_gallery_images(self):
        response = self.client.get(reverse('dashboard:buyer_detail', args=['engineering-mechanics-textbook']))
        self.assertEqual(response.status_code, 200)
        self.assertIn('images', response.context['item'])
        self.assertGreaterEqual(len(response.context['item']['images']), 2)
