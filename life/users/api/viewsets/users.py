from django.contrib.auth import get_user_model
from django.core.cache import cache
from django_filters import rest_framework as filters
from dry_rest_permissions.generics import DRYPermissions
from rest_framework import filters as rest_framework_filters
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.viewsets import GenericViewSet

from life.users.api.serializers.user import UserCreateSerializer, UserListSerializer, UserSerializer

User = get_user_model()


def remove_facility_user_cache(user_id):
    key = "user_facilities:" + str(user_id)
    cache.delete(key)
    return True


def inverse_choices(choices):
    output = {}
    for choice in choices:
        output[choice[1]] = choice[0]
    return output


INVERSE_USER_TYPE = inverse_choices(User.TYPE_CHOICES)


class UserFilterSet(filters.FilterSet):
    first_name = filters.CharFilter(field_name="first_name", lookup_expr="icontains")
    last_name = filters.CharFilter(field_name="last_name", lookup_expr="icontains")
    username = filters.CharFilter(field_name="username", lookup_expr="icontains")
    phone_number = filters.CharFilter(field_name="phone_number", lookup_expr="icontains")
    last_login = filters.DateFromToRangeFilter(field_name="last_login")
    district_id = filters.NumberFilter(field_name="district_id", lookup_expr="exact")

    def get_user_type(
        self, queryset, field_name, value,
    ):
        if value:
            if value in INVERSE_USER_TYPE:
                return queryset.filter(user_type=INVERSE_USER_TYPE[value])
        return queryset

    user_type = filters.CharFilter(method="get_user_type", field_name="user_type")


class UserViewSet(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, GenericViewSet,
):
    """
    A viewset for viewing and manipulating user instances.
    """

    queryset = User.objects.filter(is_superuser=False).select_related("local_body", "district", "state")
    lookup_field = "username"

    permission_classes = (
        IsAuthenticated,
        DRYPermissions,
    )
    filter_backends = (
        filters.DjangoFilterBackend,
        rest_framework_filters.OrderingFilter,
    )
    filterset_class = UserFilterSet
    ordering_fields = ["id", "date_joined", "last_login"]
    # last_login
    # def get_permissions(self):
    #     return [
    #         DRYPermissions(),
    #         IsAuthenticated(),
    #     ]
    # if self.request.method == "POST":
    #     return [
    #         DRYPermissions(),
    #     ]
    # else:
    #     return [
    #         IsAuthenticated(),
    #         DRYPermissions(),
    #     ]

    def get_serializer_class(self):
        if self.action == "list" and not self.request.user.is_superuser:
            return UserListSerializer
        elif self.action == "add_user":
            return UserCreateSerializer
        # elif self.action == "create":
        #     return SignUpSerializer
        else:
            return UserSerializer

    @action(detail=False, methods=["GET"])
    def getcurrentuser(self, request):
        return Response(
            status=status.HTTP_200_OK, data=UserSerializer(request.user, context={"request": request}).data,
        )

    @action(detail=True, methods=["PATCH"], permission_classes=[IsAuthenticated])
    def pnconfig(self, request, *args, **kwargs):
        user = request.user
        acceptable_fields = ["pf_endpoint", "pf_p256dh", "pf_auth"]
        for field in acceptable_fields:
            if field in request.data:
                setattr(user, field, request.data[field])
        user.save()
        return Response(stauts=status.HTTP_200_OK)
