from datetime import timedelta

"""drf imports"""
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied

"""drf_spectacular imports"""
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

"""django imports """
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils import timezone

"""local imports"""
from .models import CustomUser, EmailVerificationModel, PasswordResetCodeModel
from .serializer import (
    RegisterSerializer,
    LoginSerializer,
    VerificationSerializer,
    ResendCodeSerializer,
    PasswordResetRequestSerialiazer,
    PasswordResetSerialiazer,
)
from .uitls import generate_strong_6_digit_number, send_verification_email


@extend_schema(tags=["account"])
class RegisterUser(CreateAPIView):
    """
    View to register users in the system using

    * email: user@example.cpm
    * username: 3-8 char only letters, numbers, underscores, and dots are allowed.
    * password: Minimun 8 char

    On success verification code is sent to user email
    """

    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        verification_code = generate_strong_6_digit_number()
        code_data = EmailVerificationModel.objects.create(
            user=serializer.instance, code=verification_code
        )

        # Custom response data
        custom_data = {
            "registration_success": True,
            "message": "Account created successfully.",
            "email": serializer.data["email"],
            "username": serializer.data["username"],
        }

        headers = self.get_success_headers(serializer.data)

        return Response(custom_data, status=status.HTTP_201_CREATED, headers=headers)


@extend_schema(tags=["account"])
class LoginUser(APIView):
    """
    View to log users in the system using

    * email
    * password
    """

    serializer_class = LoginSerializer

    def post(self, request):

        serializer_class = LoginSerializer(
            data=request.data, context={"request": request}
        )

        serializer_class.is_valid(raise_exception=True)

        user = serializer_class.validated_data["user"]

        full_user_data = CustomUser.objects.filter(email=user.email).values()

        user_data = full_user_data.first()

        user_data_returned = {
            "id": user_data["id"],
            "email": user_data["email"],
            "username": user_data["username"],
            "is_staff": user_data["is_staff"],
            "is_superuser": user_data["is_superuser"],
            "is_verified": user_data["is_verified"],
        }

        # issue JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user_data": user_data_returned,
            },
            status=status.HTTP_200_OK,
        )


# ---------------------------------
@extend_schema(
    tags=["verification"],
    responses={
        200: OpenApiResponse(description="Email verified"),
        404: OpenApiResponse(description="Something went wrong."),
        500: OpenApiResponse(description="An unexpected error occurred while resending the verification code."),
    },
)
class Verification(APIView):
    """
    View to verify users by checking user verification code

    * email: user email they received code to
    * code: code receive to email
    """

    serializer_class = VerificationSerializer

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
            email = data.get("email")
            entered_code = data.get("code")

            user = CustomUser.objects.get(email=email)

            code_data = EmailVerificationModel.objects.get(user=user.id)

            if user.is_verified:
                return Response({"error": "User already verified"}, status=400)

            if code_data.code != entered_code:
                return Response({"error": "Invalid code"}, status=400)

            if code_data.is_expired:
                return Response({"error": "Code expired"}, status=400)
            user.code_expires_at = None

            user.is_verified = True
            user.save()

            code_data.code = None
            code_data.save()

            return Response(
                {"detail": "Email verified."},
                status=status.HTTP_200_OK,
            )
        except ObjectDoesNotExist:
            raise NotFound(detail=f"Something went wrong.", status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response(
                {
                    "detail": "An unexpected error occurred while resending the verification code.",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(
    tags=["verification"],
    responses={
        200: OpenApiResponse(description="Code sent succesfully"),
        400: OpenApiResponse(description="Invalid email"),
        404: OpenApiResponse(description="User not found"),
    },
)
class ResendCodeEmailVerificationCode(APIView):
    """
    Resend verification code to a user using their email, for eamil verification

    - email
    """

    serializer_class = ResendCodeSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        email = data.get("email")

        try:
            # Get user by email
            user = CustomUser.objects.get(email=email)

            # If already verified, don't resend
            if user.is_verified:
                return Response(
                    {"detail": "User is already verified."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Generate and save a new code if doesnt exist update otherwise
            verification_code = generate_strong_6_digit_number()

            verification_instance, created = (
                EmailVerificationModel.objects.update_or_create(
                    user=user,
                    defaults={
                        "code": verification_code,
                        "expires_at": timezone.now() + timedelta(minutes=15),
                    },
                )
            )

            # re-send email
            if send_verification_email(code=str(verification_code), email=user.email):
                # for security reasons don't let user know if email exist or not
                return Response(
                    {
                        "detail": "If this email exists, a reset code has been sent to verify yourself.",
                        "email": user.email,
                    },
                    status=status.HTTP_200_OK,
                )

        except ObjectDoesNotExist:
            raise NotFound(
                detail=f"If this email exists, a reset code has been sent to verify yourself. '{email}'."
            )

        except Exception as e:
            return Response(
                {
                    "detail": "An unexpected error occurred while resending the verification code.",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ---------------------------------
@extend_schema(tags=["password"])
class PasswordCodeResetRequest(APIView):
    """
    View to request code verification for users password reset

    - email: to recieve code
    """

    serializer_class = PasswordResetRequestSerialiazer

    def post(self, request):
        email = request.data["email"]

        try:
            # check if user exist
            user_data = CustomUser.objects.get(email=email)

            # generate new 6 digit code
            verification_code = generate_strong_6_digit_number()

            # create new PasswordResetCode object if doesnt exist
            password_reset_instance, created = (
                PasswordResetCodeModel.objects.update_or_create(
                    user=user_data,
                    defaults={
                        "code": verification_code,
                        "expires_at": timezone.now() + timedelta(minutes=15),
                    },
                )
            )

            if send_verification_email(
                code=str(verification_code),
                email=email,
            ):
                return Response(
                    {
                        "message": "If this email exists, a reset code has been sent to verify yourself."
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"error": "Something went wrong"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except ObjectDoesNotExist:
            return Response(
                {
                    "error": "If this email exists, a reset code has been sent to verify yourself."
                },
                status=400,
            )
        except Exception as e:
            return Response(
                {
                    "detail": "An unexpected error occurred, while requesting password reset code.",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(tags=["password"])
class PasswordReset(APIView):
    """
    View to rest user password in the system

    - email: user email
    - code: verification code sent to user email
    - new_password: new password user want to set
    """

    serializer_class = PasswordResetSerialiazer

    def patch(self, request):
        email = request.data["email"]
        code = request.data["code"]
        new_password = request.data["new_password"]

        try:
            # check if user exist
            user = CustomUser.objects.get(email=email)

            reset_code = PasswordResetCodeModel.objects.get(user=user.id)

            # check if code provided by user match one in password reset db
            if reset_code.code == code:
                # Hash and update new password in user db
                # set code in password reset db to NULL
                # save
                user.set_password(raw_password=new_password)
                user.is_verified = True
                user.save()

                reset_code.code = None
                reset_code.save()

                return Response(
                    {"message": "Password reset successful."}, status=status.HTTP_200_OK
                )
            else:
                return Response({"error": "Invalid code."}, status=400)

        except ObjectDoesNotExist:
            return Response(
                {"error": "Request a password reset code first before resetting"},
                status=400,
            )
        except Exception as e:
            return Response(
                {
                    "detail": "An unexpected error occurred reseting password.",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
