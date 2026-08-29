from django.http import Http404
from django.shortcuts import render


SELLERS = {
    1: {'name': 'Maria Santos', 'role': 'Teaching Staff', 'avatar': 'https://api.dicebear.com/7.x/avataaars/svg?seed=Maria'},
    2: {'name': 'Juan Reyes', 'role': 'Teaching Staff', 'avatar': 'https://api.dicebear.com/7.x/avataaars/svg?seed=Juan'},
    3: {'name': 'Mrs. Elena Gutierrez', 'role': 'Non-Teaching Staff', 'avatar': 'https://api.dicebear.com/7.x/avataaars/svg?seed=Elena'},
    4: {'name': 'Carlos Mendoza', 'role': 'Non-Teaching Staff', 'avatar': 'https://api.dicebear.com/7.x/avataaars/svg?seed=Carlos'},
    5: {'name': 'Alex Torres', 'role': 'Teaching Staff', 'avatar': 'https://api.dicebear.com/7.x/avataaars/svg?seed=Alex'},
    6: {'name': 'Dr. Patricia Lim', 'role': 'Teaching Staff', 'avatar': 'https://api.dicebear.com/7.x/avataaars/svg?seed=Patricia'},
}


def _normalize_seller_data(items):
    normalized = []
    for item in items:
        updated = dict(item)
        seller = SELLERS.get(item.get('seller_id'))
        if seller:
            updated['seller'] = seller['name']
            updated['seller_role'] = seller['role']
        normalized.append(updated)
    return normalized


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
        'seller_id': 1,
        'seller': 'Maria Santos',
        'seller_role': 'Bachelor of Science in Agricultural and Biosystems Engineering',
        'views': 34,
        'image_url': 'https://placehold.co/640x480?text=Engineering+Mechanics+Textbook',
        'images': [
            'https://placehold.co/640x480?text=Engineering+Mechanics+Textbook+Front',
            'https://placehold.co/640x480?text=Engineering+Mechanics+Textbook+Inside',
            'https://placehold.co/640x480?text=Engineering+Mechanics+Textbook+Detail',
        ],
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
        'seller_id': 2,
        'seller': 'Juan Reyes',
        'seller_role': 'Bachelor of Science in Information Technology',
        'views': 61,
        'image_url': 'https://placehold.co/640x480?text=Scientific+Calculator',
        'images': [
            'https://placehold.co/640x480?text=Scientific+Calculator+Front',
            'https://placehold.co/640x480?text=Scientific+Calculator+Side',
            'https://placehold.co/640x480?text=Scientific+Calculator+Case',
        ],
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
        'seller_id': 3,
        'seller': 'Mrs. Elena Gutierrez',
        'seller_role': 'Bachelor of Early Childhood Education',
        'views': 12,
        'image_url': 'https://placehold.co/640x480?text=PE+Uniform',
        'images': [
            'https://placehold.co/640x480?text=PE+Uniform+Front',
            'https://placehold.co/640x480?text=PE+Uniform+Back',
            'https://placehold.co/640x480?text=PE+Uniform+Fit',
        ],
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
        'seller_id': 4,
        'seller': 'Carlos Mendoza',
        'seller_role': 'Bachelor of Elementary Education',
        'views': 48,
        'image_url': 'https://placehold.co/640x480?text=Desk+Lamp',
        'images': [
            'https://placehold.co/640x480?text=Desk+Lamp+Front',
            'https://placehold.co/640x480?text=Desk+Lamp+Glow',
            'https://placehold.co/640x480?text=Desk+Lamp+Side',
        ],
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
        'seller_id': 5,
        'seller': 'Alex Torres',
        'seller_role': 'Bachelor of Secondary Education – English',
        'views': 27,
        'image_url': 'https://placehold.co/640x480?text=Mobile+WiFi',
        'images': [
            'https://placehold.co/640x480?text=Mobile+WiFi+Front',
            'https://placehold.co/640x480?text=Mobile+WiFi+Display',
            'https://placehold.co/640x480?text=Mobile+WiFi+Setup',
        ],
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
        'seller_id': 6,
        'seller': 'Dr. Patricia Lim',
        'seller_role': 'Bachelor of Secondary Education – Filipino',
        'views': 19,
        'image_url': 'https://placehold.co/640x480?text=Resume+Editing+Service',
        'images': [
            'https://placehold.co/640x480?text=Resume+Editing+Service+Cover',
            'https://placehold.co/640x480?text=Resume+Editing+Service+Mockup',
            'https://placehold.co/640x480?text=Resume+Editing+Service+Checklist',
        ],
        'description': 'Professional resume polishing and internship application support for students seeking internships or jobs.',
        'highlights': ['CV review', 'ATS-friendly format', 'Fast turnaround'],
    },
    {
        'id': 7,
        'slug': 'calculus-textbook',
        'title': 'Calculus Textbook (Stewart)',
        'category': 'Textbooks',
        'price': 550,
        'price_label': '₱550',
        'condition': 'Like new',
        'location': '3 mins away',
        'seller_id': 1,
        'seller': 'Maria Santos',
        'seller_role': 'Bachelor of Science in Agricultural and Biosystems Engineering',
        'views': 28,
        'image_url': 'https://placehold.co/640x480?text=Calculus+Textbook',
        'images': [
            'https://placehold.co/640x480?text=Calculus+Textbook+Cover',
            'https://placehold.co/640x480?text=Calculus+Textbook+Inside',
        ],
        'description': 'Early Transcendentals edition. Used for only one semester, practically new.',
        'highlights': ['Early Transcendentals', 'One semester use', 'Clean pages'],
    },
    {
        'id': 8,
        'slug': 'programming-book-python',
        'title': 'Python Programming Book',
        'category': 'Textbooks',
        'price': 380,
        'price_label': '₱380',
        'condition': 'Good',
        'location': '8 mins away',
        'seller_id': 2,
        'seller': 'Juan Reyes',
        'seller_role': 'Bachelor of Science in Information Technology',
        'views': 45,
        'image_url': 'https://placehold.co/640x480?text=Python+Programming',
        'images': [
            'https://placehold.co/640x480?text=Python+Programming+Cover',
            'https://placehold.co/640x480?text=Python+Programming+Pages',
        ],
        'description': 'Complete guide to Python programming. Great for beginners and intermediate programmers.',
        'highlights': ['Python 3', 'Practical examples', 'Exercise solutions included'],
    },
    {
        'id': 9,
        'slug': 'mechanical-pencil-set',
        'title': 'Mechanical Pencil Set',
        'category': 'Electronics',
        'price': 350,
        'price_label': '₱350',
        'condition': 'New',
        'location': '8 mins away',
        'seller_id': 2,
        'seller': 'Juan Reyes',
        'seller_role': 'Bachelor of Science in Information Technology',
        'views': 33,
        'image_url': 'https://placehold.co/640x480?text=Mechanical+Pencils',
        'images': [
            'https://placehold.co/640x480?text=Mechanical+Pencils+Set',
            'https://placehold.co/640x480?text=Mechanical+Pencils+Detail',
        ],
        'description': 'High-quality mechanical pencil set with extra leads. Perfect for engineering and technical drawing.',
        'highlights': ['5 pencils', 'Extra leads included', 'Precision tips'],
    },
    {
        'id': 10,
        'slug': 'pe-uniform-large',
        'title': 'PE Uniform (Large)',
        'category': 'Uniforms',
        'price': 250,
        'price_label': '₱250',
        'condition': 'New',
        'location': '5 mins away',
        'seller_id': 3,
        'seller': 'Mrs. Elena Gutierrez',
        'seller_role': 'Bachelor of Early Childhood Education',
        'views': 19,
        'image_url': 'https://placehold.co/640x480?text=PE+Uniform+Large',
        'images': [
            'https://placehold.co/640x480?text=PE+Uniform+Large+Front',
            'https://placehold.co/640x480?text=PE+Uniform+Large+Back',
        ],
        'description': 'Brand new PE uniform in size large. Never worn. Perfect condition.',
        'highlights': ['New', 'Size Large', 'Official USeP design'],
    },
    {
        'id': 11,
        'slug': 'monitor-lamp',
        'title': 'Monitor Lamp (USB)',
        'category': 'Dorm essentials',
        'price': 650,
        'price_label': '₱650',
        'condition': 'Good',
        'location': '11 mins away',
        'seller_id': 4,
        'seller': 'Carlos Mendoza',
        'seller_role': 'Bachelor of Elementary Education',
        'views': 37,
        'image_url': 'https://placehold.co/640x480?text=Monitor+Lamp',
        'images': [
            'https://placehold.co/640x480?text=Monitor+Lamp+Front',
            'https://placehold.co/640x480?text=Monitor+Lamp+Setup',
        ],
        'description': 'USB-powered monitor lamp. Reduces screen glare and eye strain during long study sessions.',
        'highlights': ['USB powered', 'Reduces glare', 'Adjustable brightness'],
    },
    {
        'id': 12,
        'slug': 'usb-charger-cable',
        'title': 'USB-C Multi-Charger',
        'category': 'Electronics',
        'price': 450,
        'price_label': '₱450',
        'condition': 'New',
        'location': '10 mins away',
        'seller_id': 5,
        'seller': 'Alex Torres',
        'seller_role': 'Bachelor of Secondary Education – English',
        'views': 52,
        'image_url': 'https://placehold.co/640x480?text=USB+Charger',
        'images': [
            'https://placehold.co/640x480?text=USB+Charger+Front',
            'https://placehold.co/640x480?text=USB+Charger+Cables',
        ],
        'description': 'Compact multi-port USB-C charger that powers multiple devices simultaneously.',
        'highlights': ['4 ports', 'Fast charging', 'Compact design'],
    },
    {
        'id': 13,
        'slug': 'career-coaching-session',
        'title': 'Career Coaching Session',
        'category': 'Services',
        'price': 500,
        'price_label': '₱500/session',
        'condition': 'Available',
        'location': '1-2 days',
        'seller_id': 6,
        'seller': 'Dr. Patricia Lim',
        'seller_role': 'Bachelor of Secondary Education – Filipino',
        'views': 24,
        'image_url': 'https://placehold.co/640x480?text=Career+Coaching',
        'images': [
            'https://placehold.co/640x480?text=Career+Coaching+Session',
        ],
        'description': '1-hour personalized career guidance and mentorship session. Help with internship prep and career planning.',
        'highlights': ['1-hour session', 'Personalized', 'Expert guidance'],
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
    seller_id = request.GET.get('seller')
    items = _filter_listings(query=query, category=category)
    seller_profile = None

    if seller_id:
        try:
            seller_id_int = int(seller_id)
            seller_profile = SELLERS.get(seller_id_int, {})
            items = [item for item in items if item.get('seller_id') == seller_id_int]
        except (TypeError, ValueError):
            pass

    items = _normalize_seller_data(items)
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
            'seller_filter': seller_id,
            'seller_profile': seller_profile,
        }
    )


def setup_buyer_item_detail(request, item_slug):
    item = next((listing for listing in FAKE_LISTINGS if listing['slug'] == item_slug), None)
    if not item:
        raise Http404('Listing not found.')

    seller_id = item.get('seller_id')
    seller_info = SELLERS.get(seller_id, {})
    item = dict(item)
    item['seller'] = seller_info.get('name', item.get('seller'))
    item['seller_role'] = seller_info.get('role', item.get('seller_role'))

    other_products = [
        p for p in FAKE_LISTINGS
        if p.get('seller_id') == seller_id and p['slug'] != item_slug
    ]
    other_products = _normalize_seller_data(other_products)

    return render(
        request,
        'buyer/buyer-detail.html',
        {
            'item': item,
            'seller_info': seller_info,
            'other_products': other_products,
            'categories': BUYER_CATEGORIES,
            'selected_category': item['category'].lower().replace(' ', '-'),
            'query': request.GET.get('q', ''),
        }
    )


def setup_buyer_cart(request):
    return render(request, 'buyer/buyer-cart.html')