from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'event'
urlpatterns = [
    path('create/', login_required(views.CreateEventWizard.as_view()), name='create'),
    path('<int:event_id>/', views.view, name='view'),
    path('join/<int:group_id>/', views.join, name='join'),
    path('join_confirmation/', views.join_confirmation, name='join_confirmation'),
    path('leave/<int:event_id>/', views.leave, name='leave'),
    path('leave_confirmation/', views.leave_confirmation, name='leave_confirmation')
]
