from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('admin/collect_data/', views.collect_data, name='collect_data'),
    path('admin/train_model/', views.train_model, name='train_model'),

]
