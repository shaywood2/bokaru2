from django.urls import path

from . import views

app_name = 'web'
urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('search/<str:place_name>/', views.search_by_place, name='search_by_place'),
    path('my_events/', views.my_events, name='my_events'),
    path('my_matches/', views.my_matches, name='my_matches'),
    path('terms_of_service/', views.terms_of_service, name='terms_of_service'),
    path('how_it_works/', views.how_it_works, name='how_it_works'),
    path('privacy_statement/', views.privacy_statement, name='privacy_statement'),
    path('refund_policy/', views.refund_policy, name='refund_policy'),
    path('about_us/', views.about_us, name='about_us')
]
