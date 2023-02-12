from django.urls import path
from . import views


urlpatterns = [
    path('', views.login),
    path('deploy', views.deploy_tokens),
    path('withdraw', views.withdraw_tokens),
    path('remove', views.remove_cost_center),
    path('modify', views.update_cost_centers),
    path('default', views.create_default_distribution),
    path('send', views.send_token_to),
    path('events', views.events)
]