from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import transaction
from rest_framework import exceptions, serializers

from life.users.api.serializers.lsg import DistrictSerializer, LocalBodySerializer, StateSerializer
from life.users.models import GENDER_CHOICES
from life.utils.serializer.phonenumber_ispossible_field import PhoneNumberIsPossibleField
from config.serializers import ChoiceField

User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    user_type = ChoiceField(choices=User.TYPE_CHOICES)
    gender = ChoiceField(choices=GENDER_CHOICES)
    password = serializers.CharField(write_only=True)
    phone_number = PhoneNumberIsPossibleField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "user_type",
            "ward",
            "local_body",
            "district",
            "state",
            "phone_number",
            "gender",
            "age",
        )

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data.get("password"))
        return super().create(validated_data)


class UserCreateSerializer(SignUpSerializer):
    password = serializers.CharField(required=False)

    class Meta:
        model = User
        exclude = (
            "is_superuser",
            "is_staff",
            "is_active",
            "last_login",
            "date_joined",
            "verified",
            "deleted",
            "groups",
            "user_permissions",
        )

    def create(self, validated_data):
        user = User.objects.create_user(**{**validated_data, "verified": True})
        user.set_password(validated_data["password"])


class UserSerializer(SignUpSerializer):
    user_type = ChoiceField(choices=User.TYPE_CHOICES, read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)

    local_body_object = LocalBodySerializer(source="local_body", read_only=True)
    district_object = DistrictSerializer(source="district", read_only=True)
    state_object = StateSerializer(source="state", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "user_type",
            "local_body",
            "district",
            "state",
            "phone_number",
            "gender",
            "age",
            "is_superuser",
            "verified",
            "local_body_object",
            "district_object",
            "state_object",
        )
        read_only_fields = ("is_superuser", "verified", "user_type", "ward", "local_body", "district", "state")

    extra_kwargs = {"url": {"lookup_field": "username"}}


class UserBaseMinimumSerializer(serializers.ModelSerializer):
    user_type = ChoiceField(choices=User.TYPE_CHOICES, read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "username",
            "email",
            "last_name",
            "user_type",
            "last_login",
        )


class UserListSerializer(serializers.ModelSerializer):
    local_body_object = LocalBodySerializer(source="local_body", read_only=True)
    district_object = DistrictSerializer(source="district", read_only=True)
    state_object = StateSerializer(source="state", read_only=True)
    user_type = ChoiceField(choices=User.TYPE_CHOICES, read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "username",
            "local_body_object",
            "district_object",
            "state_object",
            "user_type",
            "last_login",
        )

