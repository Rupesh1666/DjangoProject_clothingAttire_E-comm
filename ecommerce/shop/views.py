


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Order, OrderItem, ShippingAddress

def store(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'shop/store.html', context)

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    order, created = Order.objects.get_or_create(user=request.user, complete=False)
    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
    
    if not created:
        order_item.quantity += quantity
    else:
        order_item.quantity = quantity
    
    order_item.save()
    
    return redirect('cart')

@login_required
def update_cart(request, item_id):
    order_item = get_object_or_404(OrderItem, id=item_id, order__user=request.user, order__complete=False)
    quantity = int(request.POST.get('quantity', order_item.quantity))
    if quantity > 0:
        order_item.quantity = quantity
        order_item.save()
    else:
        order_item.delete()
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    order_item = get_object_or_404(OrderItem, id=item_id, order__user=request.user, order__complete=False)
    order_item.delete()
    return redirect('cart')

@login_required
def cart(request):
    customer = request.user
    order, created = Order.objects.get_or_create(user=customer, complete=False)
    items = order.orderitem_set.all()
    
    context = {'items': items, 'order': order}
    return render(request, 'shop/cart.html', context)

@login_required
def checkout(request):
    customer = request.user
    order, created = Order.objects.get_or_create(user=customer, complete=False)
    items = order.orderitem_set.all()

    if request.method == 'POST':
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zipcode = request.POST.get('zipcode')

        if address and city and state and zipcode:
            shipping_address = ShippingAddress(
                user=customer,
                order=order,
                address=address,
                city=city,
                state=state,
                zipcode=zipcode
            )
            shipping_address.save()
            order.complete = True
            order.save()

            messages.success(request, 'Your order has been placed successfully!')
            return redirect('store')
        else:
            messages.error(request, 'Please fill in all the required fields.')

    context = {'items': items, 'order': order}
    return render(request, 'shop/checkout.html', context)

def services(request):
    return render(request, 'shop/services.html')
