from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("won_view", views.won_view, name="won_view"),
    path("display_listing/<str:plisting>", views.display_listing, name="display_listing"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("watchlist/<str:plisting>", views.watchlist, name="watchlist"),
    path("bid/<str:plisting>", views.bid, name="bid"),
    path("remove_auction/<str:plisting>", views.remove_auction, name="remove_auction"),
    path("end_auction/<str:plisting>", views.end_auction, name="end_auction"),
]
