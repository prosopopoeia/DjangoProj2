from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("display_listing/<str:listing>", views.display_listing, name="display_listing"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("watchlist/<str:plisting>/<str:puser>", views.watchlist, name="watchlist"),
    path("watchlist/<str:user>", views.watchlist, name="watchlist"),
]
