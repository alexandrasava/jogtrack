import logging

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView, GenericAPIView,\
    ListCreateAPIView, RetrieveDestroyAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.authentication import token_expire_handler
from utils.filters.commons import FilterListMixin
from utils.filters.parser import ParsingException
from users.models import User
from users.permissions import UserIsAuthority, UserCanRUD
from users.serializers import UserSerializer, UserLoginSerializer,\
    TokenSerializer
from utils.permissions import is_admin


logger = logging.getLogger('jogtrack')
logger.setLevel(logging.DEBUG)


class UserRegistrationView(CreateAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        user = serializer.instance
        token, _ = Token.objects.get_or_create(user=user)
        data = serializer.data

        # Add token info to the data.
        token_data = TokenSerializer(token).data
        for token_key in token_data:
            data[token_key] = token_data[token_key]

        return Response(data, status=status.HTTP_201_CREATED)


class UserLoginView(GenericAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.user
            token, _ = Token.objects.get_or_create(user=user)
            is_expired, token = token_expire_handler(token)

            return Response(
                data=TokenSerializer(token).data,
                status=status.HTTP_200_OK
            )

        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def get_queryset(self):
        filters = self.get_search_filters()

        if is_admin(self.request.user):
            qs = Jog.objects.all()
            if filters:
                return qs.filter(filters)
            return qs
        else:
            qs = Jog.objects.filter(user=self.request.user)
            if filters:
                return qs.filter(filters)
            return qs


class UserListCreateView(ListCreateAPIView, FilterListMixin):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, UserIsAuthority]
    filter_fields = {
        'id': int,
        'role': int,
        'username': str,
        'email': str,
    }

    def get_queryset(self):
        filters = self.get_search_filters()

        qs = User.objects.all()
        if filters:
            return qs.filter(filters)
        return qs

    def list(self, request, *args, **kwargs):
        """ This is called on GET requests."""
        try:
            response = super().list(request, *args, **kwargs)
        except ParsingException as err:
            return Response(
                str(err),
                status=status.HTTP_400_BAD_REQUEST
            )

        return response


class UserRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, UserCanRUD]
