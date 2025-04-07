{% extends 'store/base.html' %}
{% load static %}

{% block title %}{{ product.name }} - ABUZADA STORE{% endblock %}

{% block content %}
<div class="product-detail">
  <h1>{{ product.name }}</h1>
  <p class="price">{{ product.price }} ₽</p>

  <!-- Контейнер под основное фото + миниатюры -->
  <div class="product-images">
    {% with main_photo=product.images.filter(is_main=True).first %}
      {% if main_photo %}
        <!-- Есть фото с is_main=True -->
        <img
          id="mainImage"
          class="main-image"
          src="{{ main_photo.image.url }}"
          alt="{{ product.name }} main"
        />
      {% else %}
        <!-- Если нет is_main, берём просто первую картинку -->
        {% with first_photo=product.images.first %}
          {% if first_photo %}
            <img
              id="mainImage"
              class="main-image"
              src="{{ first_photo.image.url }}"
              alt="{{ product.name }} first"
            />
          {% else %}
            <!-- fallback: нет фотографий вообще -->
            <img
              id="mainImage"
              class="main-image"
              src="{% static 'store/images/no_image.png' %}"
              alt="No image"
            />
          {% endif %}
        {% endwith %}
      {% endif %}
    {% endwith %}

    <!-- Миниатюры -->
    <div class="thumbnail-container">
      {% for pimg in product.images.all %}
        <!-- Проверим, если pimg – та же, что уже вывели как main? 
             Но для упрощения выведем все, пусть swap перемещает. -->
        <img
          class="thumbnail"
          src="{{ pimg.image.url }}"
          alt="{{ product.name }} thumb {{ forloop.counter }}"
        />
      {% endfor %}
    </div>
  </div>

  <!-- Прочая инфа: вкладки, цвета, размеры -->
  <div class="product-info">
    <!-- Цвета (если нужны) -->
    <div class="color-section">
      <p>Цвет:</p>
      <div class="color-options">
        <!-- Если сейчас нет реальных файлов под каждый цвет, 
             вы можете просто оставить статические data-front / data-back 
             или убрать этот блок. -->
        <span
          class="color-swatch active-color"
          data-front="{% static 'store/images/MessiFront.PNG' %}"
          data-back="{% static 'store/images/MessiBack.PNG' %}"
          style="background-color: #ffffff;"
        ></span>
        <!-- ... и т.д. ... -->
      </div>
    </div>

    <!-- Выбор размера -->
    <div class="size-section">
      <p>Размер:</p>
      <div class="size-options">
        <button class="size-button" data-size="S">S</button>
        <button class="size-button" data-size="M">M</button>
        <button class="size-button" data-size="L">L</button>
        <button class="size-button" data-size="XL">XL</button>
      </div>
    </div>

    <!-- Кнопка в корзину -->
    <button class="add-to-cart-button">Добавить в корзину</button>

    <!-- Вкладки (Описание / Additional Info) -->
    <div class="tab-container">
      <button class="tab-button active" data-tab="description">Описание</button>
      <button class="tab-button" data-tab="additional">Additional Info</button>
    </div>
    <div class="tab-content">
      <div class="tab-panel" id="description">
        {% if product.description %}
          <p>{{ product.description }}</p>
        {% else %}
          <p>Описание не указано</p>
        {% endif %}
      </div>
      <div class="tab-panel hidden" id="additional">
        {% if product.additional_info %}
          <p>{{ product.additional_info }}</p>
        {% else %}
          <p>Нет дополнительной информации</p>
        {% endif %}
      </div>
    </div>
  </div>
</div>

<!-- Рекомендации -->
{% if recommended_products %}
<div class="recommended-products">
  <h2>Вам могут понравиться</h2>
  <div class="recommended-grid">
    {% for rec in recommended_products %}
      <div class="recommended-item">
        <a href="{% url 'product_detail' rec.slug %}">
          <!-- Если у rec есть хотя бы одна картинка, берём её -->
          {% with rec_first=rec.images.first %}
            {% if rec_first %}
              <img src="{{ rec_first.image.url }}" alt="{{ rec.name }}" />
            {% else %}
              <img src="{% static 'store/images/no_image.png' %}" alt="No image" />
            {% endif %}
          {% endwith %}
          <p>{{ rec.name }}</p>
          <p>{{ rec.price }} ₽</p>
        </a>
      </div>
    {% endfor %}
  </div>
</div>
{% endif %}
{% endblock %}