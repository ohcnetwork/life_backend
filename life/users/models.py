from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.urls import reverse


def reverse_choices(choices):
    output = {}
    for choice in choices:
        output[choice[0]] = choice[1]
    return output


GENDER_CHOICES = [(1, "Male"), (2, "Female"), (3, "Non-binary")]
REVERSE_GENDER_CHOICES = reverse_choices(GENDER_CHOICES)

phone_number_regex = RegexValidator(
    regex=r"^((\+91|91|0)[\- ]{0,1})?[456789]\d{9}$",
    message="Please Enter 10/11 digit mobile number or landline as 0<std code><phone number>",
    code="invalid_mobile",
)

DISTRICT_CHOICES = [
    (1, "Thiruvananthapuram"),
    (2, "Kollam"),
    (3, "Pathanamthitta"),
    (4, "Alappuzha"),
    (5, "Kottayam"),
    (6, "Idukki"),
    (7, "Ernakulam"),
    (8, "Thrissur"),
    (9, "Palakkad"),
    (10, "Malappuram"),
    (11, "Kozhikode"),
    (12, "Wayanad"),
    (13, "Kannur"),
    (14, "Kasargode"),
]


class State(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"


class District(models.Model):
    state = models.ForeignKey(State, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"


LOCAL_BODY_CHOICES = (
    # Panchayath levels
    (1, "Grama Panchayath"),
    (2, "Block Panchayath"),
    (3, "District Panchayath"),
    # Municipality levels
    (10, "Municipality"),
    # Corporation levels
    (20, "Corporation"),
    # Unknown
    (50, "Others"),
)


def reverse_lower_choices(choices):
    output = {}
    for choice in choices:
        output[choice[1].lower()] = choice[0]
    return output


REVERSE_LOCAL_BODY_CHOICES = reverse_lower_choices(LOCAL_BODY_CHOICES)


class LocalBody(models.Model):
    district = models.ForeignKey(District, on_delete=models.PROTECT)

    name = models.CharField(max_length=255)
    body_type = models.IntegerField(choices=LOCAL_BODY_CHOICES)
    localbody_code = models.CharField(max_length=20, blank=True)

    class Meta:
        unique_together = (
            "district",
            "body_type",
            "name",
        )

    def __str__(self):
        return f"{self.name} ({self.body_type})"


class Ward(models.Model):
    local_body = models.ForeignKey(LocalBody, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    number = models.IntegerField()

    class Meta:
        unique_together = (
            "local_body",
            "name",
            "number",
        )

    def __str__(self):
        return f"{self.name}"


class User(AbstractUser):

    ward = models.ForeignKey(Ward, on_delete=models.PROTECT, null=True, blank=True)
    local_body = models.ForeignKey(LocalBody, on_delete=models.PROTECT, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.PROTECT, null=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.PROTECT, null=True, blank=True)

    phone_number = models.CharField(max_length=14, validators=[phone_number_regex])
    gender = models.IntegerField(choices=GENDER_CHOICES, blank=False)
    age = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    verified = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    # Notification Data
    pf_endpoint = models.TextField(default=None, null=True)
    pf_p256dh = models.TextField(default=None, null=True)
    pf_auth = models.TextField(default=None, null=True)

    REQUIRED_FIELDS = [
        "email",
        "phone_number",
        "age",
        "gender",
        "district",
    ]

