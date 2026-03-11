from django.urls import path
from .views import HomeView, DashboardView, upload_audio, ResultDetailView, signup_view, login_view, logout_view

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('upload/', upload_audio, name='upload'),
    path('result/<int:pk>/', ResultDetailView.as_view(), name='result_detail'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]
