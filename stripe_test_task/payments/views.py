import stripe
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse

from .models import Item, Order


def item_detail(request, id):
    """
    Displays a detail page for a single item with a Stripe Checkout button.
    """
    item = get_object_or_404(Item, pk=id)
    return render(request, 'payments/item.html', {
        'item': item,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY
    })


def buy_item(request, id):
    """
    Creates a Stripe Checkout Session for purchasing a single item.
    Returns the session ID in JSON format.
    """
    item = get_object_or_404(Item, pk=id)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': item.currency,
                'product_data': {
                    'name': item.name,
                    'description': item.description,
                },
                'unit_amount': int(item.price * 100),
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri(reverse('success')),
        cancel_url=request.build_absolute_uri(reverse('cancel'))
    )
    return JsonResponse({'id': session.id})


def order_detail(request, id):
    """
    Displays an order detail page including all items, tax, and discount.
    """
    order = get_object_or_404(Order, pk=id)
    return render(request, 'payments/order.html', {
        'order': order,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY
    })


def buy_order(request, id):
    """
    Creates a Stripe Checkout Session for purchasing an entire order,
    including multiple items, optional discount, and tax.
    Returns the session ID in JSON format.
    """
    order = get_object_or_404(Order, pk=id)
    currency = order.currency
    stripe.api_key = settings.STRIPE_SECRET_KEY

    item_currencies = set(item.currency for item in order.items.all())
    if len(item_currencies) != 1:
        return JsonResponse({'error': 'All items in the order must have the same currency'}, status=400)

    line_items = []
    for item in order.items.all():
        line_items.append({
            'price_data': {
                'currency': currency,
                'product_data': {
                    'name': item.name,
                    'description': item.description,
                },
                'unit_amount': int(item.price * 100),
            },
            'quantity': 1,
        })

    discounts = []
    if order.discount:
        coupon = stripe.Coupon.create(
            percent_off=order.discount.percent_off,
            duration='once'
        )
        promo_code = stripe.PromotionCode.create(coupon=coupon.id)
        discounts.append({'promotion_code': promo_code.id})

    tax_rates = []
    if order.tax:
        tax_rate = stripe.TaxRate.create(
            display_name=order.tax.name,
            percentage=float(order.tax.percentage),
            inclusive=False,
        )
        tax_rates.append(tax_rate.id)

    for item in line_items:
        if tax_rates:
            item['tax_rates'] = tax_rates

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        discounts=discounts if discounts else None,
        mode='payment',
        success_url=request.build_absolute_uri(reverse('success')),
        cancel_url=request.build_absolute_uri(reverse('cancel'))
    )

    return JsonResponse({'id': session.id})


def show_success_page(request):
    """Displays a page for the successful payment usecase."""
    return render(request, 'payments/success.html')


def show_cancellation_page(request):
    """Displays a page for the cancelled payment usecase."""
    return render(request, 'payments/cancel.html')
