from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_bag, name='bag'),
    path('add/<int:portion_id>/', views.add_to_bag, name='add_to_bag'),
    path('adjust/<int:portion_id>/', views.adjust_bag, name='adjust_bag'),
    path('remove/<int:portion_id>/', views.remove_from_bag, name='remove_from_bag')
]
