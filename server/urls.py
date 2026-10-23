from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from dealership import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('dealers/<int:dealer_id>/', views.dealer_detail, name='dealer_detail'),
    path('dealers/state/<str:state>/', views.home_by_state, name='home_by_state'),
    path('dealers/<int:dealer_id>/review/', views.review_form, name='review_form'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_page, name='logout'),
    path('register/', views.register_page, name='register'),
    path('about/', RedirectView.as_view(url='/static/About.html', permanent=False)),
    path('contact/', RedirectView.as_view(url='/static/Contact.html', permanent=False)),
    path('api/dealerships/', views.api_dealers, name='api_dealers'),
    path('api/dealerships/<int:dealer_id>/', views.api_dealer, name='api_dealer'),
    path('api/dealerships/state/<str:state>/', views.api_dealers_by_state, name='api_dealers_by_state'),
    path('api/reviews/dealer/<int:dealer_id>/', views.api_dealer_reviews, name='api_dealer_reviews'),
    path('api/reviews/', views.api_add_review, name='api_add_review'),
    path('api/car-makes/', views.api_car_makes, name='api_car_makes'),
    path('api/sentiment/', views.api_sentiment, name='api_sentiment'),
    path('api/auth/csrf/', views.api_csrf, name='api_csrf'),
    path('api/auth/me/', views.api_me, name='api_me'),
    path('api/auth/login/', views.api_login, name='api_login'),
    path('api/auth/logout/', views.api_logout, name='api_logout'),
    path('api/auth/register/', views.api_register, name='api_register'),
    # Useful course-style aliases backed by the same working Django API.
    path('djangoapp/get_dealers', views.api_dealers),
    path('djangoapp/get_dealers/<str:state>', views.api_dealers_by_state),
    path('djangoapp/dealer/<int:dealer_id>', views.api_dealer),
    path('djangoapp/get_dealer_reviews/<int:dealer_id>', views.api_dealer_reviews),
    path('djangoapp/get_cars', views.api_car_makes),
    path('djangoapp/analyze_review', views.api_sentiment),
]
