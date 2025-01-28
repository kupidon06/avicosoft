import uuid
from decimal import Decimal
from datetime import datetime,timedelta


from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Sum,F
from apps.users.models import User, Fournisseur
from django.utils.timezone import now
from django.utils import timezone

# Models
class Building(models.Model):
    name = models.CharField(max_length=100)
    details = models.TextField()
    capacity = models.IntegerField()
    photo = models.ImageField(upload_to='building_photos/', null=True, blank=True)

    def __str__(self):
        return self.name

    def get_availability(self):
        """
        Calcule la disponibilité restante en fonction des lots actifs dans ce bâtiment.
        """
        active_batches = self.batch_set.filter(status='active')
        total_current_poultry = sum(batch.get_available_poultry() for batch in active_batches)

        # Calculer la disponibilité
        availability = self.capacity - total_current_poultry
        return max(availability, 0)

class Breed(models.Model):
    name = models.CharField(max_length=100)
    details = models.TextField()
    photo = models.ImageField(upload_to='breed_photos/', null=True, blank=True)

    def __str__(self):
        return self.name


class Batch(models.Model):
    # Constants
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('quarantine', 'Quarantine'),
    ]

    # Fields
    name = models.CharField(max_length=100, blank=True, editable=False)
    breed = models.ForeignKey(Breed, on_delete=models.CASCADE)
    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    arrival_date = models.DateField()
    arrival_age = models.IntegerField(default=0)
    arrival_quantity = models.IntegerField(default=0)  # Nombre initial de poules
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    details = models.TextField(blank=True, null=True)

    # String representation
    def __str__(self):
        return self.name

    # Validation
    def clean(self):
        """
        Vérifie la validité des données, notamment la capacité du bâtiment.
        """
        super().clean()

        # Vérifie que la date d'arrivée n'est pas dans le futur
        if self.arrival_date > timezone.now().date():
            raise ValidationError({'arrival_date': 'The arrival date cannot be in the future.'})

        # Vérifie la capacité du bâtiment
        if self.building:
            active_batches = Batch.objects.filter(
                building=self.building,
                status='active'
            ).exclude(id=self.id)  # Exclut le batch actuel lors de la modification

            total_poultry = sum(batch.arrival_quantity for batch in active_batches)
            projected_total = total_poultry + self.arrival_quantity

            if projected_total > self.building.capacity:
                raise ValidationError({
                    'arrival_quantity': (
                        f"Adding this batch exceeds the building's capacity. "
                        f"Current: {total_poultry}, Proposed: {projected_total}, "
                        f"Max: {self.building.capacity}."
                    )
                })

    # Save logic
    def save(self, *args, **kwargs):
        """
        Génère un nom unique si nécessaire, valide le modèle, et le sauvegarde.
        """
        if not self.name:
            self.name = self.generate_name()
        self.full_clean()
        super().save(*args, **kwargs)

    def generate_name(self):
        """
        Génère un nom unique pour chaque lot basé sur la date d'arrivée.
        """
        today = timezone.now().strftime('%Y%m%d')
        batch_count = Batch.objects.filter(arrival_date=self.arrival_date).count() + 1
        return f"Batch-{today}-{batch_count}"

    def get_current_age(self):
        """
        Retourne l'âge actuel du lot en jours ou en semaines en fonction de l'âge d'arrivée.
        """
        today = timezone.now().date()
        days_since_arrival = (today - self.arrival_date).days
        current_age = self.arrival_age + days_since_arrival

        return {
            'days': current_age,
            'weeks': current_age // 7
        }

    # Calculs sur les quantités
    def get_deceased_quantity(self):
        """
        Retourne le nombre total de poules décédées.
        """
        return self.dailylog_set.aggregate(
            total_deceased=models.Sum('deceased_quantity')
        )['total_deceased'] or 0

    def get_sick_quantity(self):
        """
        Retourne le nombre de poules malades en se basant sur le dernier log quotidien.
        """
        last_log = self.dailylog_set.order_by('-log_date').first()
        return last_log.sick_quantity if last_log else 0

    def get_current_poultry(self):
        """
        Retourne le nombre total actuel de poules (hors décès).
        """
        return self.arrival_quantity - self.get_deceased_quantity()

    def get_available_poultry(self):
        """
        Calcule le nombre actuel de poules disponibles en tenant compte des allocations.
        """
        allocated_poultry = self.batch_allocations.aggregate(
            total_allocated=models.Sum('quantity_poultry')
        )['total_allocated'] or 0

        return self.get_current_poultry() - allocated_poultry

    def get_total_eggs_collected(self):
        """
        Retourne le total des œufs collectés pour ce lot.
        """
        return self.eggcollection_set.aggregate(
            total_eggs=models.Sum('quantity')
        )['total_eggs'] or 0

    def get_available_eggs(self):
        """
        Retourne le nombre d'œufs disponibles en tenant compte des allocations.
        """
        allocated_eggs = self.batch_allocations.aggregate(
            total_allocated=models.Sum('quantity_eggs')
        )['total_allocated'] or 0

        return self.get_total_eggs_collected() - allocated_eggs

    # Revenus
    def get_revenue_from_eggs(self):
        """
        Retourne le revenu total généré par les œufs dans ce lot.
        """
        allocations = self.batch_allocations.filter(quantity_eggs__isnull=False)
        return sum(
            allocation.quantity_eggs * allocation.order_item.product_unit.price
            for allocation in allocations
        )

    def get_revenue_from_poultry(self):
        """
        Retourne le revenu total généré par les poules dans ce lot.
        """
        allocations = self.batch_allocations.filter(quantity_poultry__isnull=False)
        return sum(
            allocation.quantity_poultry * allocation.order_item.product_unit.price
            for allocation in allocations
        )

    def get_total_revenue(self):
        """
        Retourne le revenu total généré par ce lot (œufs + poules).
        """
        return self.get_revenue_from_eggs() + self.get_revenue_from_poultry()

    # Dépenses
    def get_total_expenses(self):
        """
        Calcule le total des dépenses associées à ce batch.
        """
        return self.expense_set.aggregate(
            total=models.Sum('amount')
        )['total'] or 0

    # Rentabilité
    def calculate_profitability(self):
        """
        Calcule la profitabilité en soustrayant les dépenses des revenus totaux.
        """
        total_revenue = self.get_total_revenue()
        total_expenses = self.get_total_expenses()
        return {
            'total_revenue': total_revenue,
            'total_expenses': total_expenses,
            'profitability': total_revenue - total_expenses
        }

    # Taux de mortalité
    def get_mortality_rate(self):
        """
        Calcule le taux de mortalité.
        """
        deceased_quantity = self.get_deceased_quantity()
        initial_quantity = self.arrival_quantity
        return (deceased_quantity / initial_quantity) * 100 if initial_quantity > 0 else 0

    # Taux de ponte
    def get_laying_rate(self):
        """
        Calcule le taux de ponte.
        """
        total_eggs = self.get_total_eggs_collected()
        current_poultry = self.get_current_poultry()
        return (total_eggs / current_poultry) * 100 if current_poultry > 0 else 0

    # Suivi de la nutrition
    def get_nutrition_data(self):
        """
        Retourne les données de nutrition.
        """
        nutrition_logs = self.feeding_set.all()
        return [
            {
                'date': log.feeding_date,
                'feed_type': log.feed_type.name,
                'quantity': log.quantity
            }
            for log in nutrition_logs
        ]


    def calculate_monthly_profitability(self):
        """
        Calcule la rentabilité par mois en soustrayant les dépenses des revenus mensuels.
        """
        monthly_profitability = []
        current_date = self.arrival_date
        end_date = timezone.now().date()

        while current_date <= end_date:
            month_start = current_date.replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            total_revenue = self.get_total_revenue_for_period(month_start, month_end)
            total_expenses = self.get_total_expenses_for_period(month_start, month_end)
            profitability = total_revenue - total_expenses

            monthly_profitability.append({
                'month': month_start.strftime('%Y-%m'),
                'total_revenue': total_revenue,
                'total_expenses': total_expenses,
                'profitability': profitability
            })

            current_date = month_end + timedelta(days=1)

        return monthly_profitability

    def get_total_revenue_for_period(self, start_date, end_date):
        """
        Calcule le revenu total pour une période donnée.
        """
        egg_revenue = self.batch_allocations.filter(
            quantity_eggs__isnull=False,
            order_item__order__created_at__range=(start_date, end_date)
        ).aggregate(
            total=Sum(F('quantity_eggs') * F('order_item__product_unit__price'))
        )['total'] or 0

        poultry_revenue = self.batch_allocations.filter(
            quantity_poultry__isnull=False,
            order_item__order__created_at__range=(start_date, end_date)
        ).aggregate(
            total=Sum(F('quantity_poultry') * F('order_item__product_unit__price'))
        )['total'] or 0

        return egg_revenue + poultry_revenue

    def get_total_expenses_for_period(self, start_date, end_date):
        """
        Calcule le total des dépenses pour une période donnée.
        """
        return self.expense_set.filter(
            expense_date__range=(start_date, end_date)
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0
    


class Feed(models.Model):
    UNIT_CHOICES = (
        ('kg', 'Kilograms'),
        ('g', 'Grams'),
        ('L', 'Liters'),
        ('ml', 'Milliliters'),
        ('unit', 'Unit'),
    )
    name = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit_measure = models.CharField(max_length=10, choices=UNIT_CHOICES, default='kg')

    def __str__(self):
        return f"{self.name} ({self.unit_measure})"

class Treatment(models.Model):
    name = models.CharField(max_length=100)
    details = models.TextField()
    duration_days = models.IntegerField()

    def __str__(self):
        return self.name


class DailyLog(models.Model):
    batch = models.ForeignKey('Batch', on_delete=models.CASCADE)
    log_date = models.DateField()
    living_quantity = models.IntegerField(default=0)
    deceased_quantity = models.IntegerField(default=0)
    sick_quantity = models.IntegerField(default=0)
    details = models.TextField(blank=True)

    def __str__(self):
        return f"Daily log for {self.batch.name} on {self.log_date}"


    def save(self, *args, **kwargs):
        """
        Valide avant de sauvegarder.
        """
        
        super().save(*args, **kwargs)


class Feeding(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    feeding_date = models.DateField()
    quantity = models.FloatField()
    feed_type = models.ForeignKey(Feed, on_delete=models.CASCADE)
    details = models.TextField(blank=True)

    def __str__(self):
        return f"Feeding for {self.batch.name} on {self.feeding_date}"

    def clean(self):
        """
        Vérifie :
        - La quantité d'aliments doit être positive.
        - Le stock disponible doit suffire pour la quantité demandée.
        """
        super().clean()

        # Vérification de la quantité positive
        if self.quantity <= 0:
            raise ValidationError({'quantity': 'Quantity must be greater than zero.'})

        # Vérification du stock disponible
        if self.feed_quantity_before < self.quantity:
            raise ValidationError({
                'quantity': f'Insufficient stock for {self.feed_type.name}. Available: {self.feed_quantity_before:.2f}, required: {self.quantity:.2f}'
            })

    @property
    def feed_quantity_before(self):
        """
        Calcule le stock disponible avant cette alimentation.
        - Total des provisions ajoutées pour ce type d'aliment.
        - Moins les quantités utilisées dans les feedings précédents.
        - Moins les pertes enregistrées (StockLoss).
        """
        total_provisions = Provision.objects.filter(feed=self.feed_type).aggregate(
            total=Sum('quantity')
        )['total'] or 0

        used_feedings = Feeding.objects.filter(
            feed_type=self.feed_type,
            feeding_date__lt=self.feeding_date
        ).aggregate(total=Sum('quantity'))['total'] or 0

        # Inclure les feedings du même jour, dans l'ordre
        same_day_feedings = Feeding.objects.filter(
            feed_type=self.feed_type,
            feeding_date=self.feeding_date
        ).exclude(id=self.id).order_by('id')

        

        total_losses = StockLoss.objects.filter(feed=self.feed_type).aggregate(
            total=Sum('quantity')
        )['total'] or 0

        return total_provisions - (used_feedings + total_losses)

    @property
    def feed_quantity_after(self):
        """
        Calcule le stock restant après cette alimentation.
        """
        return self.feed_quantity_before - self.quantity

    def save(self, *args, **kwargs):
        """
        Valide les données avant de sauvegarder.
        """
        self.full_clean()  # Appelle `clean` pour validation
        super().save(*args, **kwargs)


class EggCollection(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    collection_date = models.DateField()
    quantity = models.IntegerField(default=0)
    craked = models.IntegerField(default=0)
    details = models.TextField(blank=True)

    def __str__(self):
        return f"Egg collection for {self.batch.name} on {self.collection_date}"
    def clean(self):
        super().clean()
        # Vérifie si la date de collecte est dans le futur
        if self.collection_date > timezone.now().date():
            raise ValidationError({'collection_date': 'The collection date cannot be in the future.'})


class TreatmentHistory(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    treatment = models.ForeignKey(Treatment, on_delete=models.CASCADE)
    treatment_date = models.DateField()
    details = models.TextField(blank=True)

    def __str__(self):
        return f"{self.treatment.name} for {self.batch.name} on {self.treatment_date}"


class Provision(models.Model):
    supplier = models.ForeignKey(Fournisseur, on_delete=models.CASCADE)
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    quantity = models.FloatField()
    provision_date = models.DateField(default=timezone.now)
    details = models.TextField(blank=True)

    def __str__(self):
        return f"Provision of {self.quantity} {self.feed.unit_measure} of {self.feed.name} on {self.provision_date}"



class StockLoss(models.Model):
    REASON_CHOICES = [
        ('spillage', 'Spillage'),
        ('damage', 'Damage'),
        ('expiry', 'Expiry'),
        ('theft', 'Theft'),
        ('other', 'Other'),
    ]

    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name='stock_losses')
    loss_date = models.DateField(default=timezone.now)
    quantity = models.FloatField()
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, default='other')
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Loss of {self.quantity} {self.feed.unit_measure} of {self.feed.name} on {self.loss_date} ({self.reason})"

    def clean(self):
        """Validate the loss entry."""
        super().clean()
        if self.quantity <= 0:
            raise ValidationError({'quantity': 'Loss quantity must be greater than zero.'})

        # Check available stock
        available_stock = self.calculate_available_stock()
        if self.quantity > available_stock:
            raise ValidationError({
                'quantity': f'Insufficient stock to record this loss. Available: {available_stock}, requested loss: {self.quantity}.'
            })

    def calculate_available_stock(self):
        """Calculate the available stock for the given feed."""
        total_provisions = Provision.objects.filter(feed=self.feed).aggregate(total=Sum('quantity'))['total'] or 0
        total_used = Feeding.objects.filter(feed_type=self.feed).aggregate(total=Sum('quantity'))['total'] or 0
        total_losses = StockLoss.objects.filter(feed=self.feed).exclude(id=self.id).aggregate(total=Sum('quantity'))['total'] or 0

        return total_provisions - (total_used + total_losses)

class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Expense(models.Model):
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Fournisseur, null=True, blank=True, on_delete=models.SET_NULL)
    batch = models.ForeignKey(Batch, null=True, blank=True, on_delete=models.SET_NULL)
    details = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - {self.amount} on {self.expense_date}"

class ExpensePayment(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    details = models.TextField(blank=True)

    def __str__(self):
        return f"Payment of {self.amount} for expense {self.expense}"
