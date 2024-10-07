from django.contrib import admin
from django.urls import path, re_path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from localpay.view.login_views import CustomTokenObtainPairView
from localpay.view.user_views import UserListAndCreateAPIView, UserDetailAPIView , ChangePasswordAPIView , UpdateUserAPIView
from localpay.view.pay_views import Payment

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="LocalPay API",
        default_version='v1',
        description="API documentation for LocalPay project",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@localpay.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += [
    path('users/', UserListAndCreateAPIView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserDetailAPIView.as_view(), name='user-detail'),
    path('users/<int:pk>/change_password/', ChangePasswordAPIView.as_view(), name='change-password'),
    path('users/<int:pk>/update_user/',UpdateUserAPIView.as_view(), name='update_user'),
]

urlpatterns += [
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/obtain/', TokenObtainPairView.as_view(), name='token_refresh'),
]

urlpatterns += [
    path('api/payment/', Payment.as_view(), name='payment'),
]

urlpatterns += [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
