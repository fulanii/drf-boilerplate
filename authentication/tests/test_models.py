from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError
import pytest

from authentication.models import CustomUser


@pytest.mark.django_db
class TestModels:
    def test_user_registration(self):
        instance = CustomUser.objects.create(email="a@b.com", username="v.ald_1")
        instance.set_password("strongpass123")
        instance.full_clean()
        instance.save()

        assert instance.pk is not None
        assert instance.id == 1
        assert instance.email == "a@b.com"
        assert instance.username == "v.ald_1"
        assert instance.password != "strongpass123"
    
    def test_email_code_creation(self):
        ...

    def test_rest_password_code_creation(self):
        ...