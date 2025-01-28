import json
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Order, Payment
from apps.profile.models import  PaymentIntegration
from apps.profile.providers.cinetpay import CinetPayService

@login_required(login_url='/login/')
def initiate_payment(request, order_id):
    """
    Initie un paiement pour une commande en générant une URL de paiement CinetPay
    et redirige l'utilisateur vers la passerelle.
    """
    order = get_object_or_404(Order, id=order_id)

    # Vérifier si la commande est éligible au paiement
    if order.status != "pending":
        return JsonResponse({'error': 'La commande n\'est pas éligible au paiement.'}, status=400)

    # Récupérer l'intégration CinetPay pour l'utilisateur
    user = request.user
    integration = get_object_or_404(
        PaymentIntegration, provider="cinetpay", is_active=True
    )

    # Configurer le service CinetPay
    cinetpay = CinetPayService(
        api_key=integration.api_key,
        site_id=integration.site_id,
        currency=integration.currency,
    )

    # Générer un ID de transaction unique
    transaction_id = f"order-{order.id}-{user.id}"

    try:
        # Initier le paiement
        response = cinetpay.initiate_payment(
            amount=order.debt_amount,
            transaction_id=transaction_id,
            description=f"Paiement pour la commande {order.id}",
            return_url="https://afb.pythonanywhere.com/",  # URL de retour après paiement
            notify_url="https://127.0.0.1:8000/api/orders/",  # Webhook pour confirmation
        )

        # Créer un enregistrement temporaire du paiement
        Payment.objects.create(
            order=order,
            integration=integration,
            amount=order.debt_amount,
            currency=integration.currency,
            transaction_id=transaction_id,
            payment_status='pending',
        )

        # Rediriger vers l'URL de paiement
        payment_url = response.get("data", {}).get("payment_url")
        if payment_url:
            return redirect(payment_url)
        else:
            return JsonResponse({'error': 'Échec de la génération de l\'URL de paiement.'}, status=500)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def payment_webhook(request):
    """
    Webhook pour recevoir les mises à jour des paiements depuis CinetPay.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            transaction_id = data.get('transaction_id')
            status = data.get('status')  # Statut du paiement, par exemple 'ACCEPTED'

            # Récupérer le paiement correspondant
            payment = get_object_or_404(Payment, transaction_id=transaction_id)

            if status == 'ACCEPTED':
                # Mettre à jour le statut du paiement et de la commande
                payment.payment_status = 'paid'
                payment.order.status = 'completed'
                payment.order.save()
            else:
                payment.payment_status = 'failed'

            payment.save()
            return JsonResponse({'message': 'Webhook traité avec succès.'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Méthode de requête invalide.'}, status=400)
