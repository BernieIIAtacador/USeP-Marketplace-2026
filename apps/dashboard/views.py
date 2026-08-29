from django.http import Http404
from django.shortcuts import render


FAKE_LISTINGS = [
    {
        'id': 1,
        'slug': 'engineering-mechanics-textbook',
        'title': 'Engineering Mechanics Textbook',
        'category': 'Textbooks',
        'price': 450,
        'price_label': '₱450',
        'condition': 'Good condition',
        'location': '3 mins away',
        'seller': 'Student seller',
        'views': 34,
        'image_class': 'product-image-one',
        'image_url': 'https://placehold.co/640x480?text=Engineering+Mechanics+Textbook',
        'description': '4th edition textbook with minimal highlighting. All pages are intact and the cover is still in good shape.',
        'highlights': ['4th edition', 'Minimal notes', 'All pages intact'],
    },
    {
        'id': 2,
        'slug': 'scientific-calculator',
        'title': 'Scientific Calculator',
        'category': 'Electronics',
        'price': 900,
        'price_label': '₱900',
        'condition': 'Barely used',
        'location': '8 mins away',
        'seller': 'Verified seller',
        'views': 61,
        'image_class': 'product-image-two',
        'image_url': 'https://placehold.co/640x480?text=Scientific+Calculator',
        'description': 'Casio fx-991 in excellent working condition, complete with original case and charging cable.',
        'highlights': ['Barely used', 'Original case included', 'Fully working'],
    },
    {
        'id': 3,
        'slug': 'pe-uniform-medium',
        'title': 'PE Uniform (Medium)',
        'category': 'Uniforms',
        'price': 250,
        'price_label': '₱250',
        'condition': 'Clean and wearable',
        'location': '5 mins away',
        'seller': 'Local vendor',
        'views': 12,
        'image_class': 'product-image-three',
        'image_url': 'https://placehold.co/640x480?text=PE+Uniform',
        'description': 'Campus-ready PE uniform in good condition. Clean fit, easy to wash, and comfortable for daily use.',
        'highlights': ['Comfortable fit', 'Easy to wash', 'Campus-ready'],
    },
    {
        'id': 4,
        'slug': 'study-desk-lamp',
        'title': 'Study Desk Lamp',
        'category': 'Dorm essentials',
        'price': 1200,
        'price_label': '₱1,200',
        'condition': 'Excellent condition',
        'location': '11 mins away',
        'seller': 'Student seller',
        'views': 48,
        'image_class': 'product-image-four',
        'image_url': 'https://placehold.co/640x480?text=Desk+Lamp',
        'description': 'Adjustable LED desk lamp with soft lighting for late-night study sessions and reading.',
        'highlights': ['Adjustable brightness', 'LED lighting', 'Perfect for dorm rooms'],
    },
    {
        'id': 5,
        'slug': 'mobile-wifi-device',
        'title': 'Mobile Wi-Fi Device',
        'category': 'Electronics',
        'price': 600,
        'price_label': '₱600',
        'condition': 'Good condition',
        'location': '10 mins away',
        'seller': 'Campus seller',
        'views': 27,
        'image_class': 'product-image-five',
        'image_url': 'https://placehold.co/640x480?text=Mobile+WiFi',
        'description': 'Portable internet device for travel and dorm use, tested and ready to connect with campus activities.',
        'highlights': ['Portable', 'Ready to use', 'Great for dorm internet'],
    },
    {
        'id': 6,
        'slug': 'resume-editing-service',
        'title': 'Resume Editing Service',
        'category': 'Services',
        'price': 250,
        'price_label': '₱250/hr',
        'condition': 'Available this week',
        'location': '1 day lead time',
        'seller': 'Career support',
        'views': 19,
        'image_class': 'product-image-six',
        'image_url': 'https://placehold.co/640x480?text=Resume+Editing+Service',
        'description': 'Professional resume polishing and internship application support for students seeking internships or jobs.',
        'highlights': ['CV review', 'ATS-friendly format', 'Fast turnaround'],
    },
]


BUYER_CATEGORIES = [
    {'label': 'All items', 'slug': 'all'},
    {'label': 'Textbooks', 'slug': 'textbooks'},
    {'label': 'Electronics', 'slug': 'electronics'},
    {'label': 'Uniforms', 'slug': 'uniforms'},
    {'label': 'Dorm essentials', 'slug': 'dorm-essentials'},
    {'label': 'Services', 'slug': 'services'},
]


def _build_category_options():
    counts = {'all': len(FAKE_LISTINGS)}
    for item in FAKE_LISTINGS:
        slug = item['category'].lower().replace(' ', '-')
        counts[slug] = counts.get(slug, 0) + 1

    categories = []
    for category in BUYER_CATEGORIES:
        categories.append({
            'label': category['label'],
            'slug': category['slug'],
            'count': counts.get(category['slug'], 0),
        })

    return categories


def _filter_listings(query=None, category='all'):
    filtered = list(FAKE_LISTINGS)
    query_text = (query or '').strip().lower()
    category_slug = (category or 'all').strip().lower()

    if category_slug != 'all':
        filtered = [
            item for item in filtered
            if item['category'].lower().replace(' ', '-') == category_slug
            or item['category'].lower() == category_slug
        ]

    if query_text:
        filtered = [
            item for item in filtered
            if query_text in item['title'].lower()
            or query_text in item['category'].lower()
            or query_text in item['description'].lower()
        ]

    return filtered


# Create your views here.
def setup_seller_dashboard(request):
    return render(request, 'seller/seller-dashboard.html')


def setup_buyer_dashboard(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', 'all')
    items = _filter_listings(query=query, category=category)

    categories = _build_category_options()

    return render(
        request,
        'buyer/buyer-dashboard.html',
        {
            'items': items,
            'categories': categories,
            'selected_category': category,
            'query': query,
            'category_count': len(items),
        }
    )


def setup_buyer_item_detail(request, item_slug):
    item = next((listing for listing in FAKE_LISTINGS if listing['slug'] == item_slug), None)
    if not item:
        raise Http404('Listing not found.')

    return render(
        request,
        'buyer/buyer-detail.html',
        {
            'item': item,
            'categories': BUYER_CATEGORIES,
            'selected_category': item['category'].lower().replace(' ', '-'),
            'query': request.GET.get('q', ''),
        }
    )


def setup_buyer_cart(request):
    return render(request, 'buyer/buyer-cart.html')