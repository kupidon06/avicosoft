from django.db import models
from decimal import Decimal
import uuid
from django.core.exceptions import ValidationError
from django.utils import timezone

class Coupon(models.Model):
    """Bons de réduction pouvant être appliqués aux commandes."""
    code = models.CharField(max_length=50, unique=True)
    percentage = models.FloatField(help_text="Pourcentage de réduction (exemple : 10 pour 10%)")
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    def is_valid(self):
        """Vérifie si le coupon est valide."""
        now = timezone.now()
        return self.active and self.valid_from <= now <= self.valid_to

class Order(models.Model):
    """Modèle pour les commandes."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True  # Permet de gérer les ventes sur place
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivery_address = models.TextField(null=True, blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_type = models.CharField(
        max_length=20,
        choices=[('percentage', 'Percentage'), ('amount', 'Amount')],
        default='percentage'
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)

    def calculate_total(self):
        """Calcule le total après application des remises."""
        total = sum(item.get_total_price() for item in self.order_items.all())
        if self.coupon and self.coupon.is_valid():
            discount_amount = total * (self.coupon.percentage / Decimal('100'))
        elif self.discount_type == 'percentage':
            discount_amount = total * (self.discount / Decimal('100'))
        else:
            discount_amount = self.discount
        self.total_amount = total - discount_amount
        return self.total_amount

    @property
    def paid_amount(self):
        """Calcule le montant total payé."""
        return sum(payment.amount for payment in self.payments.filter(payment_status='paid'))

    @property
    def debt_amount(self):
        """Calcule le montant restant à payer."""
        return max(self.total_amount - self.paid_amount, Decimal('0.00'))

    def save(self, *args, **kwargs):
        self.total_amount = self.calculate_total()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id} - {self.customer}"

class OrderItem(models.Model):
    """Articles individuels d'une commande."""
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    product_unit = models.ForeignKey('produits.ProductUnit', on_delete=models.CASCADE, related_name='order_items', blank=True)
    quantity = models.PositiveIntegerField(default=1)
    batches = models.ManyToManyField('ventes.BatchAllocation', related_name='order_items')

    def get_total_price(self):
        """Calcule le prix total pour cet article."""
        unit_price = self.product_unit.apply_discounts()
        return Decimal(unit_price) * self.quantity

    def __str__(self):
        return f"{self.product_unit.name} (x{self.quantity}) - {self.order}"

class BatchAllocation(models.Model):
    """Relie un article de commande à un lot spécifique et à une quantité d'œufs ou de poules allouées."""
    order_item = models.ForeignKey('ventes.OrderItem', related_name='batch_allocations', on_delete=models.CASCADE)
    batch = models.ForeignKey('management.Batch', related_name='batch_allocations', on_delete=models.CASCADE)
    quantity_eggs = models.PositiveIntegerField(null=True, blank=True)  # Quantité d'œufs allouée à cet article de commande
    quantity_poultry = models.PositiveIntegerField(null=True, blank=True)  # Quantité de poules allouée à cet article de commande

    def clean(self):
        """Vérifie la disponibilité des œufs ou des poules dans le lot pour cet article de commande."""

        # Vérification uniquement si des œufs sont alloués
        if self.quantity_eggs:
            total_requested_eggs = self.order_item.quantity * self.order_item.product_unit.quantity  # Quantité d'œufs demandée

            # Total des quantités d'œufs allouées à cet `OrderItem` dans les autres lots
            total_allocated_eggs_in_other_batches = sum(
                allocation.quantity_eggs for allocation in self.order_item.batch_allocations.exclude(batch=self.batch)
            )
            total_allocated_eggs_in_this_batch = sum(
                allocation.quantity_eggs
                for allocation in self.order_item.batch_allocations.filter(batch=self.batch)
            )

            # Vérification de la disponibilité des œufs dans le lot actuel
            available_eggs_in_batch = self.batch.get_available_eggs()

            # Calcul de la quantité allouée et de la quantité demandée
            total_allocated_eggs_in_current_batch = total_allocated_eggs_in_other_batches + total_allocated_eggs_in_this_batch + self.quantity_eggs

            if total_allocated_eggs_in_current_batch > total_requested_eggs:
                raise ValidationError(
                    f"Le total des œufs alloués dépasse la quantité demandée pour cet article de commande. "
                    f"Quantité demandée : {total_requested_eggs}, "
                    f"Quantité allouée dans les autres lots : {total_allocated_eggs_in_other_batches}, "
                    f"Quantité allouée dans ce lot : {self.quantity_eggs + total_allocated_eggs_in_this_batch}."
                )

            # Vérification de la disponibilité des œufs dans le lot
            if self.quantity_eggs > available_eggs_in_batch:
                raise ValidationError(
                    f"Il n'y a pas assez d'œufs dans le lot {self.batch.name}. "
                    f"Quantité disponible : {available_eggs_in_batch}, "
                    f"Quantité demandée : {self.quantity_eggs}."
                )

        # Vérification uniquement si des poules sont allouées
        elif self.quantity_poultry:
            total_requested_poultry = self.order_item.quantity * self.order_item.product_unit.quantity  # Quantité de poules demandée

            # Total des quantités de poules allouées à cet `OrderItem` dans les autres lots
            total_allocated_poultry_in_other_batches = sum(
                allocation.quantity_poultry for allocation in self.order_item.batch_allocations.exclude(batch=self.batch)
            )

            total_allocated_poultry_in_this_batch = sum(
                allocation.quantity_poultry
                for allocation in self.order_item.batch_allocations.filter(batch=self.batch)
            )

            # Vérification de la disponibilité des poules dans le lot actuel
            available_poultry_in_batch = self.batch.get_available_poultry()

            # Calcul de la quantité allouée et de la quantité demandée
            total_allocated_poultry_in_current_batch = total_allocated_poultry_in_other_batches + self.quantity_poultry + total_allocated_poultry_in_this_batch
            if total_allocated_poultry_in_current_batch > total_requested_poultry:
                raise ValidationError(
                    f"Le total des poules allouées dépasse la quantité demandée pour cet article de commande. "
                    f"Quantité demandée : {total_requested_poultry}, "
                    f"Quantité allouée dans les autres lots : {total_allocated_poultry_in_other_batches}, "
                    f"Quantité allouée dans ce lot : {self.quantity_poultry + total_allocated_poultry_in_this_batch}."
                )

            # Vérification de la disponibilité des poules dans le lot
            if self.quantity_poultry > available_poultry_in_batch:
                raise ValidationError(
                    f"Il n'y a pas assez de poules dans le lot {self.batch.name}. "
                    f"Quantité disponible : {available_poultry_in_batch}, "
                    f"Quantité demandée : {self.quantity_poultry}."
                )

            # Réduire le nombre de poules disponibles dans le lot
            self.batch.arrival_quantity -= self.quantity_poultry  # Réduire la quantité de poules disponibles

        else:
            raise ValidationError("Une quantité d'œufs ou de poules doit être spécifiée.")

    def save(self, *args, **kwargs):
        """Override save pour appeler la méthode clean() avant de sauvegarder et mettre à jour les quantités dans le lot."""
        # Effectuer la validation
        self.clean()

        # Sauvegarder les modifications dans le lot
        self.batch.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Batch {self.batch.name} ({self.quantity_eggs} œufs, {self.quantity_poultry} poules)"

class Payment(models.Model):
    """Modèle représentant un paiement associé à une commande."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    order = models.ForeignKey(
        'Order',  # Remplacez 'Order' par le nom réel de votre modèle de commande
        related_name='payments',
        on_delete=models.CASCADE,
        verbose_name="Commande"
    )
    integration = models.ForeignKey(
        'profile.PaymentIntegration',
        on_delete=models.PROTECT,
        related_name='payments',
        verbose_name="Intégration de paiement"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Montant",
        help_text="Montant payé ou à payer."
    )
    currency = models.CharField(
        max_length=10,
        default="USD",
        verbose_name="Devise",
        help_text="Code ISO de la devise, par exemple USD, EUR."
    )
    payment_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Statut du paiement",
        help_text="Statut actuel du paiement."
    )
    transaction_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="ID de la transaction",
        help_text="Identifiant unique de la transaction renvoyé par le fournisseur de paiement."
    )
    payment_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date du paiement",
        help_text="Date et heure à laquelle le paiement a été effectué."
    )
    failure_reason = models.TextField(
        null=True,
        blank=True,
        verbose_name="Raison de l'échec",
        help_text="Raison détaillée en cas d'échec du paiement."
    )
    metadata = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Métadonnées",
        help_text="Données supplémentaires liées au paiement (e.g., réponse du fournisseur)."
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Mis à jour le")

    def clean(self):
        """Valide les règles métier avant de sauvegarder."""
        if self.amount <= Decimal('0.00'):
            raise ValidationError("Le montant doit être supérieur à zéro.")
        if self.amount > self.order.debt_amount:
            raise ValidationError("Le montant du paiement ne peut pas excéder le montant dû pour cette commande.")

    def save(self, *args, **kwargs):
        """Valide et sauvegarde l'objet Payment."""
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment {self.transaction_id or 'N/A'} - {self.amount} {self.currency} ({self.payment_status})"

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-created_at']
