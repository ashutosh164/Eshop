from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from.forms import *
# password hashers import
from django.contrib.auth.hashers import make_password,check_password
from django.views import View
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.conf import settings


class Index(View):
    def get(self,request):
        # if session delete the it show error so we handel the situation first we make a cart
        cart = request.session.get('cart')
        if not cart:
            request.session['cart'] = {}
        categories = Category.get_all_categories()
        categoryid = request.GET.get('category')
        if categoryid:
            products = Product.get_all_products_by_categoryid(categoryid)
        else:
            products = Product.get_all_products()
        print('you are : ',
              request.session.get('email'))  # here we want to who save login. the customer save in the session
        return render(request, 'index.html', {'products': products, 'categories': categories})

    def post(self,request):
        product = request.POST.get('product')
        # remove item from our cart
        remove = request.POST.get('remove')
        # print(product) # we just check the product add in cart
        cart = request.session.get('cart')
        if cart:
            # now check the quantity of the product
            quantity = cart.get(product)
            if quantity:
                if remove:
                    if quantity <= 1:
                        cart.pop(product)
                    else:
                        cart[product] = quantity - 1
                else:
                    cart[product] = quantity + 1
            else:
                cart[product] = 1
        else:
            cart = {}
            cart[product] = 1
        request.session['cart'] = cart
        print(request.session['cart'])
        return redirect('index')


class Signup(View):
    def get(self,request):
        return render(request,'signup.html')

    def post(self,request):
        postdata = request.POST
        first_name = postdata.get('firstname')
        last_name = postdata.get('lastname')
        phone = postdata.get('phone')
        email = postdata.get('email')
        password = postdata.get('password')
        # vilaidation withiout using form.py we can create a validation manually
        # if user miss one field and re submit it erase previous data we want to avoid that problem
        # we want save our data after we face miss field error message
        value = {
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'email': email,

        }
        error_message = None

        customer = Customer(first_name=first_name,
                            last_name=last_name,
                            phone=phone,
                            email=email,
                            password=password)
        error_message = self.validateCustomer(customer)

        # saving
        if not error_message:
            print(first_name,last_name,email,password)
            # we should save a hasher password before save the form bcz we dont want admin see customers password
            customer.password = make_password(customer.password)
            customer.save()
            subject = 'welcome to my Eshop'
            message = f'Hi {customer.first_name}, thanks you for registering'
            email_from = settings.EMAIL_HOST_USER
            recipent_list = [customer.email, ]
            send_mail(subject, message, email_from, recipent_list)


            return redirect('login')
        else:

            return render(request, 'signup.html', {'error': error_message, 'value': value})

    def validateCustomer(self,customer):
        error_message = None
        if not customer.first_name:
            error_message = 'First name required'
        elif len(customer.first_name) < 4:
            error_message = 'Name must be four character or long'
        elif not customer.last_name:
            error_message = 'Last name required'
        elif len(customer.last_name) < 4:
            error_message = 'Name must be four character or long'
        elif not customer.phone:
            error_message = 'Phone number required'
        elif len(customer.phone) < 10:
            error_message = 'Phone no. should be 10'
        elif not customer.email:
            error_message = 'Emial required'
        elif len(customer.email) < 4:
            error_message = 'Email required'
        # check unique email
        elif customer.isExists():
            error_message = 'Email address already register you should try another'

        return error_message


class Login(View):
    def get(self,request):
        return render(request, 'login.html')

    def post(self,request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        customer = Customer.get_customer_by_email(email)
        error_message = None
        if customer:
            flag = check_password(password, customer.password)
            if flag:
                # save coustomer in session
                request.session['customer'] = customer.id

                return redirect('index')
            else:
                error_message = 'Email or password Invalid'
        else:
            error_message = 'Email or password Invalid'
        return render(request, 'login.html', {'error': error_message})


def logout(request):
    request.session.clear()
    return redirect('login')


# class Cart(View):
#     def get(self,request):
#
#         ids = list(request.session.get('cart').keys())
#         product = Product.get_product_by_id(ids)
#         return render(request,'cart.html',{'product':product})


# @login_required(login_url='login')
def cart(request):
    if request.method == 'GET':
        ids = list(request.session.get('cart').keys())
        product = Product.get_product_by_id(ids)
        return render(request, 'cart.html', {'product': product})


class CheckOut(View):

    def post(self,request):
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        city = request.POST.get('city')
        state = request.POST.get('state')
        dist = request.POST.get('dist')
        zipcode = request.POST.get('zipcode')
        country = request.POST.get('country')

        customer = request.session.get('customer')
        cart = request.session.get('cart')
        products = Product.get_product_by_id(list(cart.keys()))

        for product in products:
            order = Order(customer= Customer(id=customer),
                              product=product,
                              price=product.price,
                              address=address,
                              phone=phone,
                              city=city,
                              state=state,
                              dist=dist,
                              zipcode=zipcode,
                              country=country,
                              quantity= cart.get(str(product.id))
                              )
            order.save()
        request.session['cart'] = {}

        return redirect('cart')


class OrderView(View):
    def get(self,request):
        customer = request.session.get('customer')
        order = Order.get_orders_by_customer(customer)
        # print(order)

        return render(request,'order.html',{'order':order})


def bill(request):
    customer = request.session.get('customer')
    order = Order.get_orders_by_customer(customer)
    return render(request,'bill.html',{'order':order})











# def register(request):
#     form = CreateCustomer()
#     if request.method == 'POST':
#         form = CreateCustomer(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('login')
#     return render(request,'signup.html',{'form':form})
#
#
# def login(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         user = authenticate(request,email=email,password=password)
#         if user is not None:
#             login(request,user)
#             return redirect('index')
#         else:
#             return redirect('login')
#     return render(request,'login.html')


