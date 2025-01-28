from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum,Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from decimal import Decimal
from django.core.paginator import Paginator
from .models import Category, Product, ProductUnit, Discount
from .forms import CategoryForm, ProductForm, ProductUnitForm, DiscountForm
import json
from apps.users.decorators import role_required



@login_required(login_url='login')
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def category_list(request):
    query = request.GET.get('q')
    if query:
        categories = Category.objects.filter(name__icontains=query).distinct().order_by('id')
    else:
        categories = Category.objects.all().order_by('id')

    paginator = Paginator(categories, 10)  # Show 10 categories per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()

    context = {
        'categories': page_obj,
        'form': form,
    }

    return render(request, 'apps/products/categories.html', context)

@csrf_exempt
@login_required(login_url='login')
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def update_category(request, id):
    category = get_object_or_404(Category, id=id)

    if request.method == "POST":
        category.name = request.POST.get('name', category.name)
        category.description = request.POST.get('description', category.description)
        category.save()
        return redirect('category_list')

@csrf_exempt
@login_required(login_url='login')
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def delete_category(request, id):
    category = get_object_or_404(Category, id=id)
    category.delete()
    return redirect('category_list')

@csrf_exempt
@login_required(login_url='login')
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def bulk_delete_category(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            category_ids = data.get('category_ids', [])
            action = data.get('action', 'delete')

            if not category_ids:
                return JsonResponse({'status': 'error', 'message': 'Aucune catégorie sélectionnée.'}, status=400)

            elif action == 'delete':
                categories = Category.objects.filter(id__in=category_ids)
                categories_deleted, _ = categories.delete()
                return JsonResponse({'status': 'success', 'message': f'{categories_deleted} catégorie(s) supprimée(s).'})

            else:
                return JsonResponse({'status': 'error', 'message': 'Action non reconnue.'}, status=400)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée.'}, status=405)

@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def product_list(request):
    
    query = request.GET.get('q')
    category_id = request.GET.get('category')

    products_query = Q()

    if query:
        products_query &= Q(name__icontains=query)

    if category_id:
        products_query &= Q(category_id=category_id)

    products = Product.objects.filter(products_query).distinct().order_by('id')

    paginator = Paginator(products, 10)  # Show 10 products per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()

    categories = Category.objects.all()

    context = {
        'products': page_obj,
        'form': form,
        'categories': categories,
    }

    return render(request, 'apps/products/products.html', context)

@csrf_exempt
@login_required(login_url='login')
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def update_product(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        product.name = request.POST.get('name', product.name)
        product.category = get_object_or_404(Category, id=request.POST.get('category'))
        product.description = request.POST.get('description', product.description)
        product.photo = request.FILES.get('photo', product.photo)
        product.save()
        return redirect('product_list')

@csrf_exempt
@login_required(login_url='login')
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    product.delete()
    return redirect('product_list')

@csrf_exempt
@login_required(login_url='login')
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def bulk_delete_product(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_ids = data.get('product_ids', [])
            action = data.get('action', 'delete')

            if not product_ids:
                return JsonResponse({'status': 'error', 'message': 'Aucun produit sélectionné.'}, status=400)

            elif action == 'delete':
                products = Product.objects.filter(id__in=product_ids)
                products_deleted, _ = products.delete()
                return JsonResponse({'status': 'success', 'message': f'{products_deleted} produit(s) supprimé(s).'})

            else:
                return JsonResponse({'status': 'error', 'message': 'Action non reconnue.'}, status=400)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée.'}, status=405)



@login_required(login_url='login')
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def product_unit_list(request):
    query = request.GET.get('q')
    category_id = request.GET.get('category')
    discount_from = request.GET.get('discount_from')
    discount_to = request.GET.get('discount_to')

    product_units_query = Q()

    if query:
        product_units_query &= Q(name__icontains=query)

    if category_id:
        product_units_query &= Q(product__category_id=category_id)

    if discount_from and discount_to:
        product_units_query &= Q(discount__percentage__range=(discount_from, discount_to))
    elif discount_from:
        product_units_query &= Q(discount__percentage__gte=discount_from)
    elif discount_to:
        product_units_query &= Q(discount__percentage__lte=discount_to)

    product_units = ProductUnit.objects.filter(product_units_query).distinct().order_by('id')

    paginator = Paginator(product_units, 10)  # Show 10 product units per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        form = ProductUnitForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_unit_list')
    else:
        form = ProductUnitForm()

    categories = Category.objects.all()
    discounts = Discount.objects.all()
    product=Product.objects.all()

    context = {
        'product_units': page_obj,
        'products':product,
        'form': form,
        'categories': categories,
        'discounts': discounts,
    }

    return render(request, 'apps/products/product_units.html', context)

@csrf_exempt
@login_required(login_url='login')
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def update_product_unit(request, id):
    product_unit = get_object_or_404(ProductUnit, id=id)

    if request.method == "POST":
        product_unit.product = get_object_or_404(Product, id=request.POST.get('product'))
        product_unit.name = request.POST.get('name', product_unit.name)
        product_unit.quantity = request.POST.get('quantity', product_unit.quantity)
        price = request.POST.get('price')
        price = price.replace(',', '.')
        product_unit.price = Decimal(price)
            
        product_unit.discounts.set(request.POST.getlist('discounts'))
        product_unit.save()
        return redirect('product_unit_list')

@csrf_exempt
@login_required(login_url='login')
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def delete_product_unit(request, id):
    product_unit = get_object_or_404(ProductUnit, id=id)
    product_unit.delete()
    return redirect('product_unit_list')

@csrf_exempt
@login_required(login_url='login')
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def bulk_delete_product_unit(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product_unit_ids = data.get('product_unit_ids', [])
            action = data.get('action', 'delete')

            if not product_unit_ids:
                return JsonResponse({'status': 'error', 'message': 'Aucune unité de produit sélectionnée.'}, status=400)

            elif action == 'delete':
                product_units = ProductUnit.objects.filter(id__in=product_unit_ids)
                product_units_deleted, _ = product_units.delete()
                return JsonResponse({'status': 'success', 'message': f'{product_units_deleted} unité(s) de produit supprimée(s).'})

            else:
                return JsonResponse({'status': 'error', 'message': 'Action non reconnue.'}, status=400)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée.'}, status=405)


@login_required(login_url='login')
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def discount_list(request):
    query = request.GET.get('q')
    if query:
        discounts = Discount.objects.filter(name__icontains=query).distinct().order_by('id')
    else:
        discounts = Discount.objects.all().order_by('id')

    paginator = Paginator(discounts, 10)  # Show 10 discounts per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        form = DiscountForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('discount_list')
    else:
        form = DiscountForm()

    context = {
        'discounts': page_obj,
        'form': form,
    }

    return render(request, 'apps/products/discounts.html', context)

@csrf_exempt
@login_required(login_url='login')
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def update_discount(request, id):
    discount = get_object_or_404(Discount, id=id)

    if request.method == "POST":
        discount.name = request.POST.get('name', discount.name)
        percentage = request.POST.get('percentage')
        percentage = percentage.replace(',', '.')
        discount.percentage = Decimal(percentage)
        discount.save()
        return redirect('discount_list')

@csrf_exempt
@login_required(login_url='login')
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def delete_discount(request, id):
    discount = get_object_or_404(Discount, id=id)
    discount.delete()
    return redirect('discount_list')

@csrf_exempt
@login_required(login_url='login')
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def bulk_delete_discount(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            discount_ids = data.get('discount_ids', [])
            action = data.get('action', 'delete')

            if not discount_ids:
                return JsonResponse({'status': 'error', 'message': 'Aucune remise sélectionnée.'}, status=400)

            elif action == 'delete':
                discounts = Discount.objects.filter(id__in=discount_ids)
                discounts_deleted, _ = discounts.delete()
                return JsonResponse({'status': 'success', 'message': f'{discounts_deleted} remise(s) supprimée(s).'})

            else:
                return JsonResponse({'status': 'error', 'message': 'Action non reconnue.'}, status=400)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée.'}, status=405)
