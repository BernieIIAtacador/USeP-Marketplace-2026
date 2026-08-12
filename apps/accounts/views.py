from django.db import transaction
from django.db.models import F
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import update_session_auth_hash
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import User, EmailOTP
from .utils import generate_otp, send_otp_email
from throttle import check_and_hit, reset, get_client_ip, RateLimitExceeded

LOGIN_RATE_LIMIT = 5           
LOGIN_RATE_WINDOW = 300       
OTP_MAX_ATTEMPTS = 5

CHANGE_PASSWORD_RATE_LIMIT = 5
CHANGE_PASSWORD_RATE_WINDOW = 300

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

    return render(request, "verification/verify.html")


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


def get_user(request, email=None):

    email = email if email is not None else request.POST.get("email", "").strip().lower()
    password = request.POST.get("password")

    return authenticate(request, username=email, password=password)


def redirect_user(user):

    if user.is_first_login:
        return redirect("change_password")

    return redirect("dashboard")