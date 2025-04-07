from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    # Коллекции
    path('collections/goat/', views.collections_goat, name='collections_goat'),
    path('collections/elite/', views.collections_elite, name='collections_elite'),
    path('collections/legends/', views.collections_legends, name='collections_legends'),
    # Детское
    path('kids/goat/', views.kids_goat, name='kids_goat'),
    path('kids/elite/', views.kids_elite, name='kids_elite'),
    path('kids/legends/', views.kids_legends, name='kids_legends'),
    # Другие страницы
    path('promotions/', views.promotions, name='promotions'),
    path('giftcards/', views.giftcards, name='giftcards'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    path('social/', views.social, name='social'),
    # Детальная страница товара
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
]