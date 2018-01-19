from django.urls import path

from . import views

app_name = 'account'
urlpatterns = [
    path('profile', views.view, name='view'),
    path('profile/view/<str:username>', views.view_user, name='view_user'),
    path('profile/edit', views.edit, name='edit'),
    path('profile/edit/photo', views.update_photo, name='update_photo'),
    path('account', views.preferences, name='preferences'),
    path('account/payment', views.preferences_payment, name='payment'),
    path('account/payment_history', views.preferences_payment_history, name='payment_history'),
    path('account/close', views.close, name='close'),
    # Usage example: $.post( "/memo/about/2/", "lorem ipsum dolor sit amet");
    path('memo/about/<str:about_user_id>/', views.create_or_update_memo, name='memo')
]
