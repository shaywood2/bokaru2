from django.urls import path, include

from . import views, views_registration

app_name = 'account'
urlpatterns = [
    path('profile/', include([
        path('', views.view, name='view'),
        path('view/<str:username>/', views.view_user, name='view_user'),
        path('edit/', views.edit, name='edit')
    ])),
    path('account/', include([
        path('', views.preferences, name='preferences'),
        path('payment/', views.preferences_payment, name='payment'),
        path('payment_history/', views.preferences_payment_history, name='payment_history'),
        path('close/', views.close, name='close')
    ])),
    # Registration views
    path('register/', include([
        path('', views_registration.register, name='register'),
        path('join/<int:group_id>', views_registration.register_and_join_group, name='register_and_join'),
        path('done/', views_registration.register_success, name='registration_success'),
        path('activate/<str:activation_key>', views_registration.activate, name='registration_activate'),
    ])),

    # Usage example: $.post( "/memo/about/2/", "lorem ipsum dolor sit amet");
    path('memo/about/<str:about_user_id>/', views.create_or_update_memo, name='memo')
]
