import re

"""drf imports"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.validators import UniqueValidator

"""django imports"""
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from django.contrib.auth.password_validation import validate_password

"""local imports """
from .models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["email", "username", "password"]
        extra_kwargs = {
            "password": {"write_only": True},
            "username": {
                "error_messages": {
                    "max_length": "Username must be between 3 and 8 characters long."
                }
            },
        }

    # --- Custom Validation Methods ---
    def validate_password(self, value):
        try:
            validate_password(value, self.instance)
        except Exception as e:
            raise serializers.ValidationError({"password": list(e)})

        return value

    def validate_username(self, value):
        # Normalize to lowercase
        username = value.lower()

        # only letters, numbers, underscores, and dots
        if not re.match(r"^[a-zA-Z0-9_.]+$", username):
            raise serializers.ValidationError(
                "Only letters, numbers, underscores, and dots are allowed."
            )

        # Length check
        if len(username) < 3 or len(username) > 8:
            raise serializers.ValidationError(
                "Username must be between 3 to 8 characters long."
            )

        # Uniqueness check (case-insensitive)
        if CustomUser.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError("User with this username already exists.")

        return username

    def validate_email(self, value):
        # Normalize to lowercase
        email = value.lower()

        # Uniqueness check (case-insensitive)
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("User with this email already exists.")

        return email

    # over riding create so password gets hashed b4 saving in db
    def create(self, validated_data):
        user = CustomUser(
            email=validated_data["email"], username=validated_data["username"]
        )
        user.set_password(validated_data["password"])  # hashes the password
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        identifier = attrs.get("identifier")
        password = attrs.get("password")

        if not identifier or not password:
            raise serializers.ValidationError(
                "Both identifier and password are required."
            )

        if "@" in identifier:
            try:
                user_obj = CustomUser.objects.get(email__iexact=identifier)
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError("Invalid email or password.")
        else:
            try:
                user_obj = CustomUser.objects.get(username__iexact=identifier)
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError("Invalid username or password.")

        # get user data based on email/username
        user = authenticate(
            request=self.context.get("request"),
            email=user_obj.email,
            password=attrs["password"],
        )

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        attrs["user"] = user
        return attrs


class VerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.IntegerField()


class ResendCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetRequestSerialiazer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetSerialiazer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.IntegerField()
    new_password = serializers.CharField()

    def validate_new_password(self, value):
        try:
            validate_password(value, self.instance)
        except Exception as e:
            raise serializers.ValidationError({"password": list(e)})

        return value
