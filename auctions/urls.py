from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("listing/<int:listing_id>", views.listing_page, name='listing_page'),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name='create'),
    path("categories", views.categories, name='categories'),
    path("category/<int:category_id>", views.category_page, name='category_page'),
    path("watchlist", views.watchlist, name='watchlist'),
]
