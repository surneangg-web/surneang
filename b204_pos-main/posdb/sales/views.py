# sales/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Order, OrderItem, Discount
from .forms import OrderItemForm, DiscountForm


@login_required
def product_list(request):
    """បង្ហាញផលិតផល active ទាំងអស់ តម្រៀប A–Z"""
    products = Product.objects.filter(is_active=True)
    return render(request, 'sales/product_list.html', {'products': products})

@login_required
def product_detail(request, pk):
    """បង្ហាញព័ត៌មានលម្អិតសម្រាប់ផលិតផលតែមួយ។ Return 404 ប្រសិនបើរកមិនឃើញ"""
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'sales/product_detail.html', {'product': product})

@login_required
def order_list(request):
    """បង្ហាញការបញ្ជាទិញទាំងអស់ ថ្មីបំផុតមុន"""
    orders = Order.objects.all()
    return render(request, 'sales/order_list.html', {'orders': orders})

@login_required
def create_order(request):
    """Instantly create an open order and jump straight to the add-items page."""
    order = Order.objects.create(
        cashier=request.user,
        status='open',
    )
    return redirect('add_item', pk=order.pk)


@login_required
def add_item(request, pk):
    """
    Let the cashier add line items to an open order, apply discounts, then mark it paid.
    """
    order = get_object_or_404(Order, pk=pk)

    # Check if order is still open
    if order.status != 'open':
        return render(request, 'sales/add_item.html', {
            'order':          order,
            'item_form':      None,
            'discount_form':  None,
            'items':          order.items.select_related('product'),
            'error':          f"Cannot add items to {order.status} order.",
        })

    if request.method == 'POST':
        # "Cancel Order" button
        if 'cancel_order' in request.POST:
            order.status = 'cancelled'
            order.save()
            return redirect('order_list')

        # "Mark as Paid" button
        if 'mark_paid' in request.POST:
            order.status = 'paid'
            order.save()
            return redirect('order_list')

        # "Remove Discount" button
        if 'remove_discount' in request.POST:
            try:
                order.discount.delete()
            except Discount.DoesNotExist:
                pass
            return redirect('add_item', pk=order.pk)

        # Add discount
        if 'add_discount' in request.POST:
            discount_form = DiscountForm(request.POST)
            if discount_form.is_valid():
                # Delete existing discount if any
                try:
                    order.discount.delete()
                except Discount.DoesNotExist:
                    pass
                # Create new discount
                discount = discount_form.save(commit=False)
                discount.order = order
                discount.save()
                return redirect('add_item', pk=order.pk)
        else:
            discount_form = DiscountForm()

        # Add a line item
        item_form = OrderItemForm(request.POST)
        if item_form.is_valid():
            item = item_form.save(commit=False)
            item.order      = order
            item.unit_price = item.product.price   # snapshot the current price
            item.save()
            product = item.product
            product.stock -= item.quantity
            product.save()            
            return redirect('add_item', pk=order.pk)
    else:
        item_form = OrderItemForm()
        discount_form = DiscountForm()

    # Check if order has discount
    try:
        discount = order.discount
    except Discount.DoesNotExist:
        discount = None

    return render(request, 'sales/add_item.html', {
        'order':          order,
        'item_form':      item_form,
        'discount_form':  discount_form,
        'discount':       discount,
        'items':          order.items.select_related('product'),
    })

@login_required
def my_orders(request):
    orders = Order.objects.filter(cashier=request.user)
    return render(request, 'sales/order_list.html', {'orders': orders})
