from django.db import transaction
from django.db.models import F
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import User, EmailOTP
from .utils import generate_otp, send_otp_email
from throttle import check_and_hit, reset, get_client_ip, RateLimitExceeded

LOGIN_RATE_LIMIT = 5           
LOGIN_RATE_WINDOW = 300       
OTP_MAX_ATTEMPTS = 5

CHANGE_PASSWORD_RATE_LIMIT = 5
CHANGE_PASSWORD_RATE_WINDOW = 300

# Create your views here.
def setup_login_view(request):

    if request.user.is_authenticated:
        return redirect_user(request.user)

    if request.method == "POST":

        email = request.POST.get("email", "").strip().lower()
        throttle_key = f"login_throttle:{get_client_ip(request)}:{email}"

        try:
            check_and_hit(
                throttle_key,
                limit=LOGIN_RATE_LIMIT,
                window_seconds=LOGIN_RATE_WINDOW,
            )
        except RateLimitExceeded:
            messages.error(
                request,
                "Too many login attempts. Please try again in a few minutes.",
            )
            return redirect("login")

        user = get_user(request, email=email)

        if user is None:
            messages.error(request, "Email and password are incorrect.")
            return redirect("login")

        # Successful credentials clear the throttle so a legit user isn't
        # penalized by earlier typos.
        reset(throttle_key)

        if not user.email_verified:

            otp = generate_otp(user)
            request.session["pending_user_id"] = user.pk
            if otp is not None:
                send_otp_email(user, otp)
            else:
                messages.info(
                    request,
                    "A code was already sent recently — check your inbox.",
                )

            return redirect("verify")

        login(request, user)
        return redirect_user(user)

    return render(request, "accounts/login.html")


def setup_verify_view(request):

    if request.user.is_authenticated:
        return redirect_user(request.user)

    if request.method == "POST":

        entered_otp = "".join(
            request.POST.get(f"otp{i}", "") for i in range(1, 7)
        )

        user_id = request.session.get("pending_user_id")

        if not user_id:
            messages.error(request, "Your verification session has expired.")
            return redirect("login")

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            messages.error(request, "User account could not be found.")
            return redirect("login")

        verify_throttle_key = f"verify_throttle:{user_id}"

        try:
            check_and_hit(verify_throttle_key, limit=10, window_seconds=300)
        except RateLimitExceeded:
            messages.error(
                request,
                "Too many verification attempts. Please try again later.",
            )
            return redirect("login")

        with transaction.atomic():

            # select_for_update locks the row so two concurrent submits
            # can't both read attempts=4 and both slip under the cap.
            otp_record = (
                EmailOTP.objects
                .select_for_update()
                .filter(user=user, is_used=False)
                .order_by("-created_at")
                .first()
            )

            if not otp_record:
                messages.error(request, "No valid verification code found.")
                return redirect("login")

            if otp_record.expires_at < timezone.now():
                messages.error(request, "Your verification code has expired.")
                return redirect("verify")

            if otp_record.attempts >= OTP_MAX_ATTEMPTS:
                messages.error(request, "Too many verification attempts.")
                return redirect("login")

            if not check_password(entered_otp, otp_record.otp_hash):

                # Atomic increment — avoids the read-then-write race the
                # original code had under concurrent requests.
                EmailOTP.objects.filter(pk=otp_record.pk).update(
                    attempts=F("attempts") + 1
                )

                messages.error(request, "Invalid verification code.")
                return redirect("verify")

            otp_record.is_used = True
            otp_record.save(update_fields=["is_used"])

            user.email_verified = True
            user.save(update_fields=["email_verified"])

        reset(verify_throttle_key)
        login(request, user)
        request.session.pop("pending_user_id", None)
        return redirect_user(user)

    pending_user = None
    pending_user_id = request.session.get("pending_user_id")
    if pending_user_id:
        pending_user = User.objects.filter(pk=pending_user_id).first()

    return render(
        request,
        "verification/verify.html",
        {
            "pending_user": pending_user,
        },
    )


@login_required
def setup_change_password_view(request):

    if not request.user.is_first_login:
        return redirect_user(request.user)

    if request.method == "POST":

        throttle_key = f"change_password_throttle:{request.user.pk}"

        try:
            check_and_hit(
                throttle_key,
                limit=CHANGE_PASSWORD_RATE_LIMIT,
                window_seconds=CHANGE_PASSWORD_RATE_WINDOW,
            )
        except RateLimitExceeded:
            messages.error(
                request,
                "Too many attempts. Please try again in a few minutes.",
            )
            return redirect("change_password")

        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if not request.user.check_password(current_password):
            messages.error(request, "Your current password is incorrect.")
            return redirect("change_password")

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect("change_password")

        try:
            validate_password(new_password, request.user)
        except ValidationError as error:
            for message in error:
                messages.error(request, message)
            return redirect("change_password")

        # Throttle only needs to guard against wrong current_password
        # guesses — once that's confirmed, reset it like login/verify do.
        reset(throttle_key)

        request.user.set_password(new_password)
        request.user.is_first_login = False
        request.user.save(update_fields=["password", "is_first_login"])

        update_session_auth_hash(request, request.user)

        messages.success(request, "Your password has been changed successfully.")
        return redirect("dashboard")

    return render(request, "password/change-password.html")


@login_required
def dashboard_view(request):
    seller_images = request.session.get("seller_item_images", {})
    search_query = request.GET.get("q", "").strip()
    selected_category = request.GET.get("category", "").strip()
    categories = [
        {"name": "Textbooks", "icon": "TB", "count": "24 listings"},
        {"name": "Electronics", "icon": "EL", "count": "18 listings"},
        {"name": "Uniforms", "icon": "UN", "count": "12 listings"},
        {"name": "Dorm essentials", "icon": "DE", "count": "9 listings"},
    ]
    featured_items = [
        {
            "name": "Calculus: Early Transcendentals",
            "seller": "Mara D.",
            "price": "₱850",
            "condition": "Like new",
            "category": "Textbooks",
            "accent": "coral",
            "image": seller_images.get("1", f"{settings.MEDIA_URL}products/textbooks/caculus-book.jpg"),
        },
        {
            "name": "Scientific calculator",
            "seller": "Jonas R.",
            "price": "₱650",
            "condition": "Good condition",
            "category": "Electronics",
            "accent": "blue",
            "image": seller_images.get("2", f"{settings.MEDIA_URL}products/electronics/scientific-calculator.jpg"),
        },
        {
            "name": "College PE uniform set",
            "seller": "Alyssa C.",
            "price": "₱400",
            "condition": "Barely used",
            "category": "Uniforms",
            "accent": "gold",
            "image": seller_images.get("3", f"{settings.MEDIA_URL}products/uniforms/usep-uniform-set.jpg"),
        },
    ]
    if selected_category:
        featured_items = [
            item for item in featured_items
            if item["category"].lower() == selected_category.lower()
        ]
    if search_query:
        query = search_query.lower()
        featured_items = [
            item for item in featured_items
            if query in item["name"].lower()
            or query in item["category"].lower()
            or query in item["condition"].lower()
        ]
    return render(
        request,
        "accounts/dashboard.html",
        {
            "categories": categories,
            "featured_items": featured_items,
            "search_query": search_query,
            "selected_category": selected_category,
        },
    )


@login_required
def seller_view(request):
    seller_images = request.session.get("seller_item_images", {})
    selected_status = request.GET.get("status", "all")
    search_query = request.GET.get("q", "").strip()
    listings = [
        {
            "id": 1,
            "name": "Calculus: Early Transcendentals",
            "category": "Textbooks",
            "price": "₱850",
            "status": request.session.get("seller_item_statuses", {}).get("1", "Active"),
            "views": 48,
            "image": seller_images.get("1", f"{settings.MEDIA_URL}products/textbooks/caculus-book.jpg"),
        },
        {
            "id": 2,
            "name": "Scientific calculator",
            "category": "Electronics",
            "price": "₱650",
            "status": request.session.get("seller_item_statuses", {}).get("2", "Active"),
            "views": 31,
            "image": seller_images.get("2", f"{settings.MEDIA_URL}products/electronics/scientific-calculator.jpg"),
        },
        {
            "id": 3,
            "name": "College PE uniform set",
            "category": "Uniforms",
            "price": "₱400",
            "status": request.session.get("seller_item_statuses", {}).get("3", "Sold"),
            "views": 67,
            "image": seller_images.get("3", f"{settings.MEDIA_URL}products/uniforms/usep-uniform-set.jpg"),
        },
        {
            "id": 4,
            "name": "Motorcycle repair",
            "category": "Services",
            "price": "₱300 starting",
            "status": request.session.get("seller_item_statuses", {}).get("4", "Unavailable"),
            "views": 22,
            "image": seller_images.get("4", f"{settings.MEDIA_URL}services/motorcycle-repair.png"),
        },
    ]
    item_statuses = request.session.get("seller_item_statuses", {})
    custom_listings = []
    for listing in request.session.get("custom_seller_listings", []):
        listing["status"] = item_statuses.get(str(listing["id"]), listing["status"])
        custom_listings.append(listing)
    listings.extend(custom_listings)
    deleted_items = request.session.get("deleted_seller_items", [])
    listings = [listing for listing in listings if listing["id"] not in deleted_items]
    if selected_status != "all":
        listings = [
            listing for listing in listings
            if listing["status"].lower() == selected_status.lower()
        ]
    if search_query:
        listings = [
            listing for listing in listings
            if search_query.lower() in listing["name"].lower()
            or search_query.lower() in listing["category"].lower()
        ]
    all_listings = [
        {
            "status": request.session.get("seller_item_statuses", {}).get("1", "Active"),
            "views": 48,
        },
        {
            "status": request.session.get("seller_item_statuses", {}).get("2", "Active"),
            "views": 31,
        },
        {
            "status": request.session.get("seller_item_statuses", {}).get("3", "Sold"),
            "views": 67,
        },
        {
            "status": request.session.get("seller_item_statuses", {}).get("4", "Unavailable"),
            "views": 22,
        },
    ]
    all_listings.extend(
        {"status": listing["status"], "views": listing["views"]}
        for listing in request.session.get("custom_seller_listings", [])
    )
    return render(
        request,
        "accounts/seller/seller.html",
        {
            "listings": listings,
            "selected_status": selected_status,
            "search_query": search_query,
            "active_count": sum(item["status"] == "Active" for item in all_listings),
            "sold_count": sum(item["status"] == "Sold" for item in all_listings),
            "total_views": sum(item["views"] for item in all_listings),
        },
    )


@login_required
def add_listing_view(request):
    return render(request, "accounts/seller/add-listing.html")


@login_required
def manage_item_view(request, item_id):
    listings = {
        1: {
            "name": "Calculus: Early Transcendentals",
            "category": "Textbooks",
            "price": "850",
            "condition": "Like new",
            "description": "Clean copy with minimal highlighting. Great for first-year calculus classes.",
            "status": "Active",
            "views": 48,
            "image": f"{settings.MEDIA_URL}products/textbooks/caculus-book.jpg",
        },
        2: {
            "name": "Scientific calculator",
            "category": "Electronics",
            "price": "650",
            "condition": "Good condition",
            "description": "Reliable calculator with its protective case and fresh batteries.",
            "status": "Active",
            "views": 31,
            "image": f"{settings.MEDIA_URL}products/electronics/scientific-calculator.jpg",
        },
        3: {
            "name": "College PE uniform set",
            "category": "Uniforms",
            "price": "400",
            "condition": "Barely used",
            "description": "College PE uniform set in good shape.",
            "status": "Sold",
            "views": 67,
            "image": f"{settings.MEDIA_URL}products/uniforms/usep-uniform-set.jpg",
        },
        4: {
            "name": "Motorcycle repair",
            "category": "Services",
            "price": "300 starting",
            "condition": "Available by appointment",
            "description": "Basic motorcycle inspection and repair service for USeP students and staff.",
            "status": "Unavailable",
            "views": 22,
            "image": f"{settings.MEDIA_URL}services/motorcycle-repair.png",
        },
    }
    for listing in request.session.get("custom_seller_listings", []):
        listings[listing["id"]] = listing

    if item_id in request.session.get("deleted_seller_items", []):
        return redirect("seller")

    item = listings.get(item_id)
    if item is None:
        return redirect("seller")

    item_statuses = request.session.get("seller_item_statuses", {})
    item["status"] = item_statuses.get(str(item_id), item["status"])
    saved_image = request.session.get("seller_item_images", {}).get(str(item_id))
    if saved_image:
        item["image"] = saved_image
    return render(request, "accounts/seller/manage-item.html", {"item": item})


@require_POST
def logout_view(request):
    auth_logout(request)
    return render(request, "accounts/logout.html")


def get_user(request, email=None):

    email = email if email is not None else request.POST.get("email", "").strip().lower()
    password = request.POST.get("password")

    return authenticate(request, username=email, password=password)


def redirect_user(user):

    if user.is_first_login:
        return redirect("change_password")

    return redirect("dashboard")