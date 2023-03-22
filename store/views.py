import re
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import logout, login, authenticate
from .models import Customer, Product, Cart, Order
from django.views import View
from django.contrib.auth.models import User
from django.db.models import Q


def payment(request):
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    total_amount = request.POST.get('total_amount', {'totalitem':totalitem})
    # print(total_amount)
    return render(request, 'payment.html', {"total_amount":total_amount})

def success(request, id):
    user = request.user
    cart = Cart.objects.filter(user=user)
    for item in cart:
        Order(user=user, product=item.product, quantity=item.quantity).save()
        item.delete()
    # print("success")
    return redirect('/home/')

def checkout(request):
    user = request.user
    user_items = Cart.objects.filter(user=user)
    # print(user_items)
    amount = 0.0
    total_amount =0.0
    cart_product = [p for p in Cart.objects.all() if p.user == user]
    if cart_product:
        for p in cart_product:
            tempamount = (p.quantity * p.product.selling_price)
            amount += tempamount
        total_amount = amount 
    totalitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
    return render(request, 'checkout.html', {'total_amount':total_amount, 'user_items':user_items, 'totalitem':totalitem})



class home(View):
    def get(self, request):
        allproducts = Product.objects.all()
        totalitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
        return render(request, 'home.html', {'products':allproducts, 'totalitem':totalitem})
    

def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user, product=product).save()
    return redirect('/cart')
    # return HttpResponse("hello")


def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0.0
        total_amount =0.0
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        if cart_product:
            for p in cart_product:
                tempamount = (p.quantity * p.product.selling_price)
                amount += tempamount
            total_amount = amount 
            totalitem = 0
            if request.user.is_authenticated:
                totalitem = len(Cart.objects.filter(user=request.user))
            return render(request, 'addtocart.html', {'carts':cart, 'totalamount':total_amount, 'amount':amount, 'totalitem':totalitem})
        else:
            totalitem = 0
            if request.user.is_authenticated:
                totalitem = len(Cart.objects.filter(user=request.user))
            return render(request, 'empty.html', {'totalitem':totalitem})


def plus_cart(request):
    if request.method =="GET":
        # print(request.user)
        prod_id = request.GET.get('prod_id')
        # print(prod_id)
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        # print(c)
        c.quantity += 1
        c.save()
        amount = 0.0
        total_amount =0.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.selling_price)
            amount += tempamount
        total_amount = amount 
        data = {
            'quantity':c.quantity,
            'total_amount':total_amount
        }
        return JsonResponse(data)
        
def minus_cart(request):
    if request.method =="GET":
        # print(request.user)
        prod_id = request.GET.get('prod_id')
        # print(prod_id)
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        # print(c)
        c.quantity -= 1
        c.save()
        amount = 0.0
        total_amount =0.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.selling_price)
            amount += tempamount
        total_amount = amount 
        data = {
            'quantity':c.quantity,
            'total_amount':total_amount
        }
        return JsonResponse(data)

def remove_cart(request):
    if request.method =="GET":
        # print(request.user)
        prod_id = request.GET.get('prod_id')
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        amount = 0.0
        total_amount =0.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.selling_price)
            amount += tempamount
        total_amount = amount 
        data = {
            # 'quantity':c.quantity,
            'total_amount':total_amount
        }
        return JsonResponse(data)


# user register function
def signup(request):
    if request.method == "GET":
        return render(request, 'signup.html')
    else:
        postData = request.POST
        username = postData.get('username')
        email = postData.get('email')
        password = postData.get('password')

        # validations
        error_message=None
        if not username:
            error_message = 'Name required !!'
        elif len(username)<3:
            error_message = 'Name should greater than 4 !!'
        elif len(password) < 3:
            error_message = 'Password must be 6 character long !!'            
        elif not re.match("[A-Za-z0-9@#$%^&+=]",password):
            error_message = 'Your password must contain special character also [A-Za-z0-9@#$%^&+=]'
        elif not email:
            error_message = 'Email required !!'
        elif email:
            emailcheck = User.objects.filter(email=email)
            for email1 in emailcheck:
                if email1.email == email:
                    error_message = "Email already present !!"
                    break
        # value for html
        htmlvalue = {
            'usernama':username,   
            'email':email
        }
        # save data in datastore
        if not error_message:
            customer = User(
                username=username,
                email = email,
                password = make_password(password),
            )
            customer.save()
            return redirect('/login/')
        else:
            return render(request, 'signup.html', {'error':error_message,'values':htmlvalue})


def Login(request):
    if request.method == "GET":
        return render(request, 'login.html')
    else:
        email = request.POST.get('email')
        password = request.POST.get('password')
        user1 = User.objects.get(email=email)
        if user1:
            user = authenticate(username=user1.username, password=password)
            if user:
                login(request, user)                
                return redirect('/home/')
                # return HttpResponse("Every thing is great!!")
                # return redirect('/home/')
            else:
                error_msg='Email or Password is invalid !!!'
                return render(request, 'login.html', {'error_msg':error_msg})
        else:
            error_msg='Email or Password is invalid !!!'
            return render(request, 'login.html', {'error_msg':error_msg})

def Logout(request):
    logout(request)
    return redirect('/login/')