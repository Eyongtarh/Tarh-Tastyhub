from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_dishes, name='dish_list'),
    path('category/add/', views.add_category, name='add_category'),
    path('category/edit/<slug:slug>/', views.edit_category, name='edit_category'),
    path('category/delete/<slug:slug>/', views.delete_category, name='delete_category'),
    path('category/<slug:category_slug>/', views.dish_list_by_category, name='dish_list_by_category'),
    path('add/', views.add_dish, name='add_dish'),
    path('edit/<slug:slug>/', views.edit_dish, name='edit_dish'),
    path('delete/<slug:slug>/', views.delete_dish, name='delete_dish'),
    path('<slug:slug>/', views.dish_detail, name='dish_detail'),
]
