from django.urls import path
from . import views

urlpatterns=[ 
    path("login/", views.login, name= "login"),

    path('check_auth/', views.check_auth, name='check_auth'),

    path("register/", views.register, name= "register"),

    path("upload_image/", views.upload_image, name="upload_image"),

    path('csrf-token/', views.csrf_token, name='csrf_token'),

    path('check-session/', views.check_session, name='check_session'),

    path('verify/', views.verify, name='verify'),

    path('logout/', views.logout, name="logout")

    # path('check-verification/', views.check_verification, name='check_verification'),

    # path("main_page/", views.main_page, name="main_page")
]

