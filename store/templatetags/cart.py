from django import template


register = template.Library()


# call the filter use a pass a name which is u usr in template
# go to index page and see how filter load in the template
@register.filter(name='is_in_cart')
def is_in_cart(product,cart):
    keys = cart.keys()
    for id in keys:
        if int(id) == product.id:
            return True
    return False;


# filter use for how to count how many item in our cart
@register.filter(name='cart_quantity')
def cart_quantity(product,cart):
    keys = cart.keys()
    for id in keys:
        if int(id) == product.id:
            return cart.get(id)
    return 0;


@register.filter(name='total_price')
def total_price(product,cart):
    return product.price * cart_quantity(product,cart)


@register.filter(name='total_product_price')
def total_product_price(product,cart):
    sum = 0 ;
    for p in product:
        sum += total_price(p,cart)
    return sum


@register.filter(name='currency')
def currency(number):
    return '$'+str(number)


@register.filter(name='multiply')
def multiply(number,number1):
    return number * number1




