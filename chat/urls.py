from django.urls import path

from . import views

app_name = 'chat'
urlpatterns = [
    path('', views.live_event, name='live_event'),
    path('test/', views.network_test, name='network_test'),
    # ex: /chat/pick/target_user/123/event/456/response/1/
    # Responses are: 1 - Yes, 0 - No and 2 - Maybe
    path('pick/target_user/<int:target_user_id>/event/<int:event_id>/response/<int:response>/',
         views.create_pick, name='create_pick'),
    # path('test/<int:user1>/<int:user2>/', views.live_event_test)
]
