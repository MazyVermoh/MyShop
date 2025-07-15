# store/urls.py
from django.urls import path

from . import views

app_name = "store"          # даёт namespace: {% url 'store:...' %}

urlpatterns = [
    path("", views.index, name="home"),

    # товар
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),

    # коллекции
    path("collections/goat/",    views.collections_goat,    name="collections_goat"),
    path("collections/elite/",   views.collections_elite,   name="collections_elite"),
    path("collections/legends/", views.collections_legends, name="collections_legends"),

    # kids
    path("kids/goat/",    views.kids_goat,    name="kids_goat"),
    path("kids/elite/",   views.kids_elite,   name="kids_elite"),
    path("kids/legends/", views.kids_legends, name="kids_legends"),

    # страницы и акции
    path("promotions/", views.promotions, name="promotions"),
    path("giftcards/",  views.giftcards,  name="giftcards"),
    path("contacts/",   views.contacts,   name="contacts"),
    path("about/",      views.about,      name="about"),
    path("social/",     views.social,     name="social"),

    # AJAX
    path("api/subscribe/", views.subscribe, name="subscribe"),
    path(
        "ajax/product-first-image/<int:prod_id>/<int:color_id>/",
        views.product_first_image,
        name="product_first_image",
    ),
]