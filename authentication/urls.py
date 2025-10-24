from django.urls import path, include
from .views import (
    RegisterUser,
    LoginUser,
    Verification,
    ResendCodeEmailVerificationCode,
    PasswordCodeResetRequest,
    PasswordReset,
)

urlpatterns = [
    # accounts
    path("register/", RegisterUser.as_view(), name="register"),
    path("login/", LoginUser.as_view(), name="login"),
    # verifications
    path("verify-email/", Verification.as_view(), name="verify-email"),
    path(
        "resend-verification/",
        ResendCodeEmailVerificationCode.as_view(),
        name="resend-code",
    ),
    # passwords
    path(
        "reset-password-request/",
        PasswordCodeResetRequest.as_view(),
        name="reset-request",
    ),
    path("reset-password/", PasswordReset.as_view(), name="reset"),
]
