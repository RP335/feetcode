from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:problem_id>/', views.detail, name='detail'),
    path('<int:problem_id>/submit', views.submit, name='submit'),
    path('submissions',views.submissions, name="submissions"),
    path('register',views.registerPage, name="register"),
    path('login',views.loginPage, name="login"),
    path('logout',views.logoutUser, name="logout"),

]
