import datetime
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from main.forms import ProductForm
from django.urls import reverse
from django.http import HttpResponse
from django.core import serializers
from main.models import Product

# Create your views here.
@login_required(login_url='/login')
def show_main(request):
    products = Product.objects.filter(user=request.user)

    context = {
        'name': request.user.username, # Nama kamu
        'class': 'PBP A', # Kelas PBP kamu
        'app_name': 'Arto Moro PBP',
        'products': products,
        'total_products': products.__len__(),
        'last_login': request.COOKIES['last_login'],
    }

    return render(request, "main.html", context)

def create_product(request):
    form = ProductForm(request.POST or None)

    if form.is_valid() and request.method == "POST":
        product = form.save(commit=False)
        product.user = request.user
        product.save()
        return HttpResponseRedirect(reverse('main:show_main'))

    context = {'form': form}
    return render(request, "create_product.html", context)

def show_xml(request):
    data = Product.objects.all()
    return HttpResponse(serializers.serialize("xml", data), content_type="application/xml")

def show_json(request):
    data = Product.objects.all()
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

def show_xml_by_id(request, id):
    data = Product.objects.filter(pk=id)
    return HttpResponse(serializers.serialize("xml", data), content_type="application/xml")

def show_json_by_id(request, id):
    data = Product.objects.filter(pk=id)
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

def register(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been successfully created!')
            return redirect('main:login')
    context = {'form':form}
    return render(request, 'register.html', context)

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            response = HttpResponseRedirect(reverse("main:show_main")) 
            response.set_cookie('last_login', str(datetime.datetime.now()))
            return response
        else:
            messages.info(request, 'Sorry, incorrect username or password. Please try again.')
    context = {}
    return render(request, 'login.html', context)

def logout_user(request):
    logout(request)
    response = HttpResponseRedirect(reverse('main:login'))
    response.delete_cookie('last_login')
    return response

@login_required(login_url='login/')
def edit_amount(request, id, amount_change):
    product = Product.objects.get(id=id)
    # "+1" Button clicked --> Increment amount by 1
    if (amount_change == 0):
        product.amount += 1
        product.save()

    # "-1" Button clicked --> Decrement amount by 1
    elif (amount_change == 1):
        if (product.amount > 0):
            product.amount -= 1
            product.save()
        if (product.amount == 0): # jika produk sudah habis = delete
            product.delete()
        
    # "Delete Product" Button clicked --> Delete the product
    else:
        product.delete()

    return HttpResponseRedirect(reverse('main:show_main'))

def increment_product(request, product_id):
    if request.method == 'POST' and 'Tambah' in request.POST:
        product = Product.objects.get(id = product_id)
        product.amount += 1
        product.save()
    return HttpResponseRedirect(reverse('main:show_main'))

def decrement_product(request, product_id):
    if request.method == 'POST' and 'Kurang' in request.POST:
        product = Product.objects.get(id = product_id)
        if product.amount > 0 :
            product.amount -= 1
        product.save()
    return HttpResponseRedirect(reverse('main:show_main'))

def remove_product(request, product_id):
    if request.method == 'POST' and 'Hapus' in request.POST:
        product = Product.objects.get(id = product_id)
        product.delete()
    return HttpResponseRedirect(reverse('main:show_main'))

def edit_product(request, id):
    # Get product berdasarkan ID
    product = Product.objects.get(pk = id)

    # Set product sebagai instance dari form
    form = ProductForm(request.POST or None, instance=product)

    if form.is_valid() and request.method == "POST":
        # Simpan form dan kembali ke halaman awal
        form.save()
        return HttpResponseRedirect(reverse('main:show_main'))

    context = {'form': form}
    return render(request, "edit_product.html", context)

def delete_product(request, id):
    # Get data berdasarkan ID
    product = Product.objects.get(pk = id)
    # Hapus data
    product.delete()
    # Kembali ke halaman awal
    return HttpResponseRedirect(reverse('main:show_main'))