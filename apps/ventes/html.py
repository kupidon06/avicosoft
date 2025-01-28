from django.shortcuts import render, get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from openpyxl import Workbook
from .models import Order, OrderItem, Payment, Coupon,BatchAllocation
from apps.produits.models import Product, ProductUnit,Discount,Category
import json
from apps.management.models import Batch
from decimal import Decimal
from django.utils import timezone

from datetime import datetime
from apps.users.decorators import role_required

login_path = 'login'

@login_required(login_url=login_path)
def product_list(request):
    """Affiche les produits disponibles pour créer une commande."""
    categories = Category.objects.all()
    products = ProductUnit.objects.all()

    # Pagination
    paginator = Paginator(products, 10)  # 10 produits par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'apps/orders/detail.html', {'categories': categories, 'page_obj': page_obj})

@login_required(login_url=login_path)
def ecommerce(request):
    """Affiche les produits disponibles pour créer une commande."""
    categories = Category.objects.all()
    products = ProductUnit.objects.all()

    # Pagination
    paginator = Paginator(products, 10)  # 10 produits par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'apps/orders/ecom.html', {'categories': categories, 'page_obj': page_obj})



@csrf_exempt
@login_required(login_url=login_path)
@csrf_exempt
@login_required(login_url=login_path)
def filter_product_units(request):
    """
    Filtre les unités de produits (ProductUnit) en fonction des critères envoyés via POST.
    Retourne les résultats sous forme JSON avec support de filtrage par nom et pagination.
    """
    if request.method == "POST":
        # Récupérer les données de filtrage
        category_id = request.POST.get("category_id")  # ID de la catégorie
        min_price = request.POST.get("min_price")  # Prix minimum
        max_price = request.POST.get("max_price")  # Prix maximum
        name = request.POST.get("name", "").strip()  # Filtrer par nom
        page = int(request.POST.get("page", 1))  # Page actuelle
        page_size = int(request.POST.get("page_size", 10))  # Taille de la page

        # Construire la requête de filtrage
        filters = Q()
        if category_id:
            filters &= Q(product__category_id=category_id)
        if min_price:
            filters &= Q(price__gte=float(min_price))
        if max_price:
            filters &= Q(price__lte=float(max_price))
        if name:
            filters &= Q(name__icontains=name)

        # Récupérer et paginer les résultats
        product_units = ProductUnit.objects.filter(filters)
        total_count = product_units.count()  # Compter le nombre total d'éléments
        product_units = product_units[(page - 1) * page_size: page * page_size]

        # Transformer les données en JSON
        data = [
            {
                "id": unit.id,
                "name": unit.name,
                "quantity": unit.quantity,
                "price": unit.price,
                "photo": unit.product.photo.url if unit.product.photo else None
            }
            for unit in product_units
        ]

        # Renvoyer les données sous forme JSON
        return JsonResponse({
            "product_units": data,
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
        }, status=200)

    # Si la méthode n'est pas POST, renvoyer une erreur
    return JsonResponse({"error": "Invalid request method. Use POST."}, status=400)



@login_required(login_url='login')
@role_required(excluded_roles=['customer','veterinarian','employee','farmer']) 
def order_list(request):
    """Affiche la liste des commandes avec pagination."""
    order_id = request.GET.get('order_id')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    coupon_code = request.GET.get('coupon')

    orders_query = Q()

    if order_id:
        orders_query &= Q(id=order_id)

    if date_from and date_to:
        orders_query &= Q(created_at__range=[date_from, date_to])
    elif date_from:
        orders_query &= Q(created_at__gte=date_from)
    elif date_to:
        orders_query &= Q(created_at__lte=date_to)

    if coupon_code:
        orders_query &= Q(coupon__code=coupon_code)

    orders = Order.objects.filter(orders_query).order_by('-created_at')

    batches = Batch.objects.all().order_by('id')
    allocations = BatchAllocation.objects.all().order_by('id')

    # Pagination
    paginator = Paginator(orders, 10)  # 10 commandes par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'apps/orders/test.html', {'page_obj': page_obj, 'batches': batches, 'allocations': allocations})



@csrf_exempt
@role_required(excluded_roles=['customer','veterinarian','employee','farmer']) 
def create_batch_allocation(request):
    """Crée une allocation de lot pour un article de commande."""
    if request.method == 'POST':
        try:
            # Récupérer les données de la requête
            order_item_id = request.POST.get('order_item_id')
            batch_id = request.POST.get('batch_id')
            quantity_eggs = request.POST.get('quantity_eggs')
            quantity_poultry = request.POST.get('quantity_poultry')

            # Convertir les quantités en entiers
            quantity_eggs = int(quantity_eggs) if quantity_eggs else 0
            quantity_poultry = int(quantity_poultry) if quantity_poultry else 0

            # Vérifier que les IDs existent
            order_item = get_object_or_404(OrderItem, id=order_item_id)
            batch = get_object_or_404(Batch, id=batch_id)

            # Créer l'allocation de lot
            batch_allocation = BatchAllocation(
                order_item=order_item,
                batch=batch,
                quantity_eggs=quantity_eggs,
                quantity_poultry=quantity_poultry
            )

            # Sauvegarder l'allocation de lot (cela appellera la méthode clean() et mettra à jour les quantités dans le lot)
            batch_allocation.save()
            

            return JsonResponse({'status': 'success','message': '  Batch allocation created successfully', 'batch_allocation_id': str(batch_allocation.id)})

        except ValidationError as ve:
            print(f"ValidationError: {ve}")  # Log de l'erreur pour mieux comprendre
            return JsonResponse({'error': str(ve)}, status=400)

        except Exception as e:
            print(f"Error: {e}")  # Log de l'erreur pour mieux comprendre
            return JsonResponse({'error': 'Unknown error: ' + str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
@login_required(login_url=login_path)
def create_order(request):
    """Crée une nouvelle commande avec des articles."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print('Data received:', data)  # Afficher les données pour le débogage

            # Créer la commande
            order = Order.objects.create(
                customer=request.user,
                delivery_address=data.get('delivery_address'),
                coupon=data.get('coupon')
              
            )

            # Appliquer le bon de réduction si fourni
            coupon_code = data.get('coupon_code')
            if coupon_code:
                coupon = get_object_or_404(Coupon, code=coupon_code, active=True, valid_from__lte=timezone.now(), valid_to__gte=timezone.now())
                order.coupon = coupon
                order.discount = coupon.percentage
                order.discount_type = 'percentage'

            # Ajouter les articles à la commande
            items = data.get('items', [])
            for item in items:
                product_id = item.get('product_id')
                quantity = item.get('quantity', 1)
                print(f"Creating OrderItem: product_id={product_id}, quantity={quantity}")  # Log de débogage

                # Vérifiez que le product_id existe
                product_unit = get_object_or_404(ProductUnit, id=product_id)

                OrderItem.objects.create(
                    order=order,
                    product_unit=product_unit,
                    quantity=quantity
                )

            # Mise à jour du total de la commande
            order.calculate_total()
            order.save()

            return JsonResponse({'message': 'Order created successfully', 'order_id': str(order.id)})

        except Exception as e:
            print(f"Error: {e}")  # Log de l'erreur pour mieux comprendre
            return JsonResponse({'error': 'Unknown error: ' + str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)



@csrf_exempt
@login_required(login_url=login_path)
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def update_order(request, order_id):
    """Met à jour une commande existante."""
    order = get_object_or_404(Order, id=order_id)

    if request.method in ['POST', 'PUT']:
        try:
            # Utilisation correcte de request.POST.get pour récupérer les données du formulaire
            order.status = request.POST.get('status', order.status)
            order.delivery_address = request.POST.get('delivery_address', order.delivery_address)
            discount_str = request.POST.get('discount', order.discount)
            order.discount_type = request.POST.get('discount_type', order.discount_type)

            # Convert discount to Decimal
            try:
                # Remplacez la virgule par un point pour les formats de nombre français
                discount_str = discount_str.replace(',', '.')
                order.discount = Decimal(discount_str)
            except InvalidOperation:
                return JsonResponse({'error': 'Invalid discount value'}, status=400)

            # Appliquer le bon de réduction si fourni
            coupon_code = request.POST.get('coupon_code')
            if coupon_code:
                coupon = get_object_or_404(
                    Coupon,
                    code=coupon_code,
                    active=True,
                    valid_from__lte=timezone.now(),
                    valid_to__gte=timezone.now()
                )
                order.coupon = coupon
                order.discount = coupon.percentage
                order.discount_type = 'percentage'

            order.save()
            return redirect('order_list')
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return redirect('order_list')


@csrf_exempt
@login_required(login_url=login_path)
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def delete_order(request, id):
    order = get_object_or_404(Order, id=id)
    order.delete()
    return redirect('order_list')


@login_required(login_url=login_path)
def export_orders(request):
    """Exporte les commandes au format Excel."""
    orders = Order.objects.all().order_by('-created_at')
    wb = Workbook()
    ws = wb.active
    ws.title = "Orders"
    ws.append(["Order ID", "Customer", "Status", "Total Amount", "Created At"])

    for order in orders:
        ws.append([str(order.id), order.customer.username if order.customer else 'Anonymous', order.status, order.total_amount, order.created_at])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=Orders.xlsx'
    wb.save(response)
    return response

@csrf_exempt
@login_required(login_url=login_path)
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def bulk_delete_orders(request):
    """Supprime plusieurs commandes en une seule requête."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_ids = data.get('order_ids', [])
            if not order_ids:
                return JsonResponse({'status': 'error', 'message': 'No orders selected.'}, status=400)

            deleted, _ = Order.objects.filter(id__in=order_ids).delete()
            return JsonResponse({'status': 'success', 'message': f'{deleted} orders deleted.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid method.'}, status=405)


@csrf_exempt
@login_required(login_url=login_path)
def make_payment(request, order_id):
    """Enregistre un paiement pour une commande."""
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        data = json.loads(request.body)
        amount = Decimal(data.get('amount', 0))
        payment_method = data.get('payment_method')
        transaction_id = data.get('transaction_id', None)
        remark = data.get('remark', '')

        try:
            Payment.objects.create(
                order=order,
                amount=amount,
                payment_status='paid',
                payment_method=payment_method,
                transaction_id=transaction_id,
                remark=remark
            )
            return JsonResponse({'message': 'Payment recorded successfully!'})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return render(request, 'apps/ecommerce/make_payment.html', {'order': order})

@csrf_exempt
def create_order_without_user(request):
    """Crée une commande sans utilisateur."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print('Data received:', data)  # Afficher les données pour le débogage

            # Créer la commande
            order = Order.objects.create(
                status=data.get('status', 'pending'),
                delivery_address=data.get('delivery_address'),
                discount=data.get('discount', 0.00),
                discount_type=data.get('discount_type', 'percentage')
            )

            # Appliquer le bon de réduction si fourni
            coupon_code = data.get('coupon_code')
            if coupon_code:
                coupon = get_object_or_404(Coupon, code=coupon_code, active=True, valid_from__lte=timezone.now(), valid_to__gte=timezone.now())
                order.coupon = coupon
                order.discount = coupon.percentage
                order.discount_type = 'percentage'

            # Ajouter les articles à la commande
            items = data.get('items', [])
            for item in items:
                product_id = item.get('product_id')
                quantity = item.get('quantity', 1)
                print(f"Creating OrderItem: product_id={product_id}, quantity={quantity}")  # Log de débogage

                # Vérifiez que le product_id existe
                try:
                    product_unit = ProductUnit.objects.get(id=product_id)
                except ProductUnit.DoesNotExist:
                    print(f"ProductUnit with id={product_id} does not exist")  # Log de débogage
                    return JsonResponse({'error': f'ProductUnit with id={product_id} does not exist'}, status=400)

                OrderItem.objects.create(
                    order=order,
                    product_unit=product_unit,
                    quantity=quantity
                )

            # Mise à jour du total de la commande
            order.calculate_total()
            order.save()

            return JsonResponse({'message': 'Order created successfully', 'order_id': str(order.id)})

        except Exception as e:
            print(f"Error: {e}")  # Log de l'erreur pour mieux comprendre
            return JsonResponse({'error': 'Unknown error: ' + str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.is_valid():
                return JsonResponse({'success': True, 'percentage': coupon.percentage})
            else:
                return JsonResponse({'success': False, 'message': 'Coupon expiré ou inactif.'})
        except Coupon.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Coupon invalide.'})
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée.'})



@login_required(login_url='login')
def user_order_list(request):
    """Récupère les commandes d'un utilisateur précis avec pagination et filtre."""
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
   

    # Construire les filtres dynamiquement
    orders_query = Q(customer=request.user)

    if date_from and date_to:
        orders_query &= Q(created_at__range=[date_from, date_to])
    elif date_from:
        orders_query &= Q(created_at__gte=date_from)
    elif date_to:
        orders_query &= Q(created_at__lte=date_to)

    

    orders = Order.objects.filter(orders_query).order_by('-created_at')

    # Pagination
    paginator = Paginator(orders, 10)  # 10 commandes par page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Sérialisation des données
    data = {
        'orders': [
            {
                'id': str(order.id),
                'customer': str(order.customer),
                'total_amount': float(order.total_amount),
                'status': order.status,
                'created_at': order.created_at.isoformat(),
                'delivery_address': order.delivery_address,
                'coupon': order.coupon.code if order.coupon else None,
                'paid_amount':order.paid_amount or 0
            }
            for order in page_obj
        ],
        'pagination': {
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'has_previous': page_obj.has_previous(),
            'has_next': page_obj.has_next(),
        },
    }

    return JsonResponse(data, safe=False)