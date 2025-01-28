from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.core.signing import Signer, TimestampSigner, BadSignature, SignatureExpired
from django.conf import settings
from django.urls import reverse
from .models import User

signer = TimestampSigner()

@receiver(post_save, sender=User)
def send_confirmation_email(sender, instance, created, **kwargs):
    if created:  # Seulement lors de la création d'un nouvel utilisateur
        # Générer un token signé
        token = signer.sign(instance.email)
        
        # Générer le lien de confirmation
        confirmation_link = reverse('confirm_email', args=[token])
        full_link = f"{settings.SITE_URL}{confirmation_link}"

        # Envoyer l'email
        send_mail(
            subject="Confirmation de votre adresse email",
            message=f"Bonjour {instance.username},\n\nMerci de vous être inscrit. Cliquez sur le lien suivant pour confirmer votre adresse email : {full_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
        )
