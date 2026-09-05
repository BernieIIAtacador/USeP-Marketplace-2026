from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.accounts.models import User
from .models import Category, Conversation, Listing, SavedItem


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

    def test_seller_preview_supports_multiple_listings(self):
        seller = User.objects.get(email='test.seller@usep.edu.ph')
        response = self.client.get(
            reverse('dashboard:buyer'),
            {'seller': seller.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['seller_profile']['id'], seller.pk)
        self.assertGreaterEqual(response.context['items'].count(), 4)

    def test_product_media_frames_render_on_normal_and_seller_listing_pages(self):
        normal_response = self.client.get(reverse('dashboard:buyer'))
        seller = User.objects.get(email='test.seller@usep.edu.ph')
        seller_response = self.client.get(reverse('dashboard:buyer'), {'seller': seller.pk})

        self.assertContains(normal_response, 'listing-product-media')
        self.assertContains(normal_response, 'listing-seller-avatar')
        self.assertContains(seller_response, 'listing-product-media')
        self.assertContains(seller_response, 'listing-seller-avatar')

    def test_named_sellers_have_separate_linked_products(self):
        maria = User.objects.get(email='maria.santos@usep.edu.ph')
        juan = User.objects.get(email='juan.reyes@usep.edu.ph')
        self.assertEqual(maria.first_name, 'Maria')
        self.assertEqual(juan.last_name, 'Reyes')
        self.assertTrue(Listing.objects.filter(seller=maria).exists())
        self.assertTrue(Listing.objects.filter(seller=juan).exists())

    def test_buyer_cart_page_loads(self):
        response = self.client.get(reverse('dashboard:buyer_cart'))
        self.assertEqual(response.status_code, 302)

    def test_buyer_detail_has_multiple_gallery_images(self):
        response = self.client.get(reverse('dashboard:buyer_detail', args=['engineering-mechanics-textbook']))
        self.assertEqual(response.status_code, 200)
        self.assertIn('images', response.context['item'])
        self.assertGreaterEqual(len(response.context['item']['images']), 2)

    def test_seller_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard:seller'))
        self.assertEqual(response.status_code, 302)

    def test_logged_in_buyer_can_save_listing_and_start_chat(self):
        buyer = User.objects.create_user(
            email='buyer@example.com',
            password='StrongPassword123!',
            first_name='Campus',
            last_name='Buyer',
            contact_num='09123456789',
            email_verified=True,
            is_first_login=False,
        )
        listing = Listing.objects.get(slug='engineering-mechanics-textbook')
        self.client.force_login(buyer)

        save_response = self.client.post(
            reverse('dashboard:toggle_saved_item', args=[listing.slug]),
            {'next': reverse('dashboard:buyer_cart')},
        )
        self.assertEqual(save_response.status_code, 302)
        self.assertTrue(SavedItem.objects.filter(buyer=buyer, listing=listing).exists())

        chat_response = self.client.post(
            reverse('dashboard:start_conversation', args=[listing.slug]),
            {'body': 'Is this still available?'},
        )
        self.assertEqual(chat_response.status_code, 302)
        self.assertTrue(Conversation.objects.filter(buyer=buyer, listing=listing).exists())

    def test_seller_can_create_listing_for_their_account(self):
        seller = User.objects.create_user(
            email='seller@example.com',
            password='StrongPassword123!',
            first_name='Campus',
            last_name='Seller',
            contact_num='09123456788',
            email_verified=True,
            is_first_login=False,
            is_seller=True,
        )
        category = Category.objects.get(slug='textbooks')
        self.client.force_login(seller)

        response = self.client.post(reverse('dashboard:create_listing'), {
            'title': 'Database Systems',
            'category': category.pk,
            'price': '500',
            'condition': 'Good condition',
            'location': 'Library',
            'description': 'Clean copy.',
        })

        self.assertEqual(response.status_code, 302)
        created_listing = Listing.objects.get(seller=seller, title='Database Systems')
        self.assertEqual(created_listing.status, Listing.Status.ACTIVE)

    def test_seller_can_open_and_update_listing(self):
        seller = User.objects.create_user(
            email='editor@example.com',
            password='StrongPassword123!',
            first_name='Listing',
            last_name='Editor',
            contact_num='09123456787',
            email_verified=True,
            is_first_login=False,
            is_seller=True,
        )
        listing = Listing.objects.filter(seller_id__isnull=False).first()
        listing.seller = seller
        listing.save(update_fields=['seller'])
        self.client.force_login(seller)

        edit_response = self.client.get(reverse('dashboard:edit_listing', args=[listing.id]))
        self.assertEqual(edit_response.status_code, 200)

        save_response = self.client.post(reverse('dashboard:edit_listing', args=[listing.id]), {
            'title': 'Updated listing title',
            'category': listing.category_id,
            'price': '999',
            'condition': 'Like new',
            'location': 'Student center',
            'description': 'Updated details.',
            'status': Listing.Status.SOLD,
            'images': [
                SimpleUploadedFile('front.jpg', b'front-image', content_type='image/jpeg'),
                SimpleUploadedFile('back.jpg', b'back-image', content_type='image/jpeg'),
            ],
        })
        self.assertEqual(save_response.status_code, 302)
        listing.refresh_from_db()
        self.assertEqual(listing.title, 'Updated listing title')
        self.assertEqual(listing.status, Listing.Status.SOLD)
        self.assertEqual(listing.listing_images.count(), 2)

    def test_buyer_is_sent_to_buyer_dashboard_and_cannot_open_seller_dashboard(self):
        buyer = User.objects.create_user(
            email='routing-buyer@example.com',
            password='StrongPassword123!',
            first_name='Routing',
            last_name='Buyer',
            contact_num='09123456786',
            email_verified=True,
            is_first_login=False,
        )
        self.client.force_login(buyer)
        self.assertEqual(self.client.get(reverse('dashboard:seller')).url, reverse('dashboard:buyer'))

    def test_buyer_can_enable_seller_tools(self):
        buyer = User.objects.create_user(
            email='become-seller@example.com',
            password='StrongPassword123!',
            first_name='Future',
            last_name='Seller',
            contact_num='09123456784',
            email_verified=True,
            is_first_login=False,
        )
        self.client.force_login(buyer)
        response = self.client.get(reverse('dashboard:become_seller'))
        self.assertRedirects(response, reverse('dashboard:seller'))
        buyer.refresh_from_db()
        self.assertTrue(buyer.is_seller)

    def test_seller_default_landing_is_still_buyer_listings(self):
        seller = User.objects.get(email='test.seller@usep.edu.ph')
        self.client.force_login(seller)
        response = self.client.get(reverse('dashboard:buyer'))
        self.assertEqual(response.status_code, 200)

    def test_cart_contains_only_the_listings_added_by_buyer(self):
        buyer = User.objects.create_user(
            email='cart-buyer@example.com',
            password='StrongPassword123!',
            first_name='Cart',
            last_name='Buyer',
            contact_num='09123456785',
            email_verified=True,
            is_first_login=False,
        )
        listings = list(Listing.objects.filter(status=Listing.Status.ACTIVE)[:2])
        self.client.force_login(buyer)
        for listing in listings:
            self.client.post(reverse('dashboard:toggle_saved_item', args=[listing.slug]), {'next': reverse('dashboard:buyer_cart')})
        response = self.client.get(reverse('dashboard:buyer_cart'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            set(response.context['saved_items'].values_list('listing_id', flat=True)),
            {listing.id for listing in listings},
        )

    def test_carts_are_isolated_between_users(self):
        first_buyer = User.objects.create_user(
            email='first-cart-user@example.com', password='StrongPassword123!',
            first_name='First', last_name='Cart', contact_num='09123456783',
            email_verified=True, is_first_login=False,
        )
        second_buyer = User.objects.create_user(
            email='second-cart-user@example.com', password='StrongPassword123!',
            first_name='Second', last_name='Cart', contact_num='09123456780',
            email_verified=True, is_first_login=False,
        )
        first_listing, second_listing = list(Listing.objects.filter(status=Listing.Status.ACTIVE)[:2])

        self.client.force_login(first_buyer)
        self.client.post(reverse('dashboard:toggle_saved_item', args=[first_listing.slug]))
        self.client.force_login(second_buyer)
        self.client.post(reverse('dashboard:toggle_saved_item', args=[second_listing.slug]))

        first_cart = SavedItem.objects.filter(buyer=first_buyer).values_list('listing_id', flat=True)
        second_cart = SavedItem.objects.filter(buyer=second_buyer).values_list('listing_id', flat=True)
        self.assertEqual(set(first_cart), {first_listing.id})
        self.assertEqual(set(second_cart), {second_listing.id})

    def test_sold_saved_product_moves_to_sold_cart_section(self):
        buyer = User.objects.create_user(
            email='sold-cart-user@example.com', password='StrongPassword123!',
            first_name='Sold', last_name='Cart', contact_num='09123456770',
            email_verified=True, is_first_login=False,
        )
        listing = Listing.objects.filter(status=Listing.Status.ACTIVE).first()
        self.client.force_login(buyer)
        self.client.post(reverse('dashboard:toggle_saved_item', args=[listing.slug]))
        listing.status = Listing.Status.SOLD
        listing.save(update_fields=['status'])

        response = self.client.get(reverse('dashboard:buyer_cart'))
        self.assertEqual(response.context['active_saved_items'].count(), 0)
        self.assertEqual(response.context['sold_saved_items'].count(), 1)

        remove_response = self.client.post(
            reverse('dashboard:toggle_saved_item', args=[listing.slug]),
            {'next': reverse('dashboard:buyer_cart')},
        )
        self.assertRedirects(remove_response, reverse('dashboard:buyer_cart'))
        self.assertFalse(SavedItem.objects.filter(buyer=buyer, listing=listing).exists())

    def test_available_cart_item_has_message_button_but_sold_item_does_not(self):
        buyer = User.objects.create_user(
            email='cart-message-user@example.com', password='StrongPassword123!',
            first_name='Cart', last_name='Message', contact_num='09123456779',
            email_verified=True, is_first_login=False,
        )
        available, sold = list(Listing.objects.filter(status=Listing.Status.ACTIVE)[:2])
        sold.status = Listing.Status.SOLD
        sold.save(update_fields=['status'])
        SavedItem.objects.create(buyer=buyer, listing=available)
        SavedItem.objects.create(buyer=buyer, listing=sold)
        self.client.force_login(buyer)

        response = self.client.get(reverse('dashboard:buyer_cart'))
        self.assertContains(response, 'cart-message-button')
        sold_section = response.content.decode().split('Sold products', 1)[1]
        self.assertNotIn('cart-message-button', sold_section)

    def test_owner_sees_edit_link_on_listing_detail(self):
        seller = User.objects.get(email='test.seller@usep.edu.ph')
        listing = Listing.objects.filter(seller=seller).first()
        self.client.force_login(seller)
        response = self.client.get(reverse('dashboard:buyer_detail', args=[listing.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['can_edit'])

    def test_owner_edit_link_targets_dashboard_manage_modal(self):
        seller = User.objects.get(email='test.seller@usep.edu.ph')
        listing = Listing.objects.filter(seller=seller).first()
        self.client.force_login(seller)
        response = self.client.get(reverse('dashboard:buyer_detail', args=[listing.slug]))
        self.assertContains(response, 'id="open-detail-edit"')
        self.assertContains(response, 'id="detail-edit-modal"')
        self.assertContains(response, f'action="/dashboard/seller/listings/{listing.id}/edit/"')
