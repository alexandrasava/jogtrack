from django.urls import path
from users.views import UserRegistrationView, UserLoginView, UserListCreateView,\
    UserRetrieveUpdateDestroyView

app_name = 'users'

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name="register"),
    path('login/', UserLoginView.as_view(), name="login"),
    path('', UserListCreateView.as_view(), name="list_create"),
    path('<int:pk>/', UserRetrieveUpdateDestroyView.as_view(), name="user_rud")
]
