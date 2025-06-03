from django.urls import path
from . import views

urlpatterns = [
    path('item/<int:id>/', views.item_detail, name='item_detail'),
    path('buy/<int:id>/', views.buy_item, name='buy_item'),
    path('order/<int:id>/', views.order_detail, name='order_detail'),
    path('buy_order/<int:id>/', views.buy_order, name='buy_order'),
    path('success/', views.show_success_page, name='success'),
    path('cancel/', views.show_cancellation_page, name='cancel')
]