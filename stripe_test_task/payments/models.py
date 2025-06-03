from decimal import Decimal

from django.db import models


class Item(models.Model):
    """
    Represents a product that can be purchased via Stripe.
    """
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=10, default='usd')  # (e.g. 'usd', 'eur')

    def __str__(self):
        return f'Item "{self.name}"'


class Discount(models.Model):
    """
    Represents a discount that can be applied to an order.
    """
    name = models.CharField(max_length=255)
    percent_off = models.PositiveIntegerField()

    def __str__(self):
        return f'Discount "{self.name}", {self.percent_off}%'


class Tax(models.Model):
    """
    Represents a tax that can be applied to an order
    """
    name = models.CharField(max_length=255)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f'Tax "{self.name}", {self.percentage}%'


class Order(models.Model):
    """
    Represents a customer order containing multiple items and optional discount/tax.
    """
    items = models.ManyToManyField(Item, related_name='orders')
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)
    tax = models.ForeignKey(Tax, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def currency(self):
        currencies = set(item.currency for item in self.items.all())
        return currencies.pop() if len(currencies) == 1 else 'usd'

    @property
    def total_amount(self):
        total = sum(item.price for item in self.items.all())
        if self.discount:
            total *= Decimal(1 - self.discount.percent_off / 100)
        if self.tax:
            total *= Decimal(1 + float(self.tax.percentage) / 100)
        return round(total, 2)

    def __str__(self):
        return f'Order #{self.pk}: {", ".join(item.name for item in self.items.all())}'
