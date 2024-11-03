from django.contrib import admin
from django.urls import path, re_path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import permissions
from localpay.views.user_views.user_views import UserListAPIView, UpdateUserAPIView , CreateUserAPIView , DeleteUserAPIView , UserDetailAPIView 
from localpay.views.payment_views.unloading_payments import  CombinedPaymentComparisonView
from localpay.views.user_views.login_views import CustomTokenObtainPairView
from localpay.views.payment_views.payment import PaymentCreateAPIView , PaymentUpdateAPIView
from localpay.views.payment_views.payment_history import PaymentHistoryListAPIView , UserPaymentHistoryListAPIView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from localpay.views.mobile.user_payment import MobileUserPaymentHistoryListAPIView
from localpay.views.mobile.user_detail import MobileUserDetailAPIView 
from localpay.views.mobile.check_ls import AccountCheckView

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

    path('api/create-payment/', PaymentCreateAPIView.as_view(), name='create-payment'), 
    path('api/payment-history/', PaymentHistoryListAPIView.as_view(), name='payment-history'),
    
    
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('api/payment_update/<int:pk>/',PaymentUpdateAPIView.as_view(), name = 'update_payment')]


urlpatterns+= [
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/obtain/', TokenObtainPairView.as_view(), name='token_refresh'),]


urlpatterns += [
    path('user/create/',CreateUserAPIView.as_view(), name='user-create'),
    path('api/user/payment-comparison/', CombinedPaymentComparisonView.as_view(), name='payment-compare')]


urlpatterns += [
    path('users/<int:pk>/', UserDetailAPIView.as_view(), name='user-detail'),
    path('users/', UserListAPIView.as_view(), name='user-list-create'),
    path('users/<int:pk>/update_user/',UpdateUserAPIView.as_view(), name='update_user'),
    path('user/<int:pk>/delete_user/',DeleteUserAPIView.as_view(), name='delete-user'),
    path('user-payments/<int:user_id>/', UserPaymentHistoryListAPIView.as_view(), name='user-payment-history'),
    ]


urlpatterns += [
    path('mobile/user-payments/', MobileUserPaymentHistoryListAPIView.as_view() , name='mobile-user-payments'),
    path('mobile/user-detail/', MobileUserDetailAPIView.as_view(), name='mobile-user-detail'),
    path('api/check-account/',AccountCheckView.as_view(), name='check_account')
    ]