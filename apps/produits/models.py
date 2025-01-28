from django.db import models

class Category(models.Model):
    """Catégories de produits (exemple : Volaille, Grains, Oeufs)."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    """Produit générique avec des unités et des remises."""
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    description = models.TextField(blank=True)
    photo = models.ImageField(upload_to="product_photos/", null=True, blank=True)

    def __str__(self):
        return self.name


class ProductUnit(models.Model):
    """Unités de vente pour un produit, chacune avec un prix spécifique."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="units")
    name = models.CharField(max_length=100)  # Exemple : "Petit casier", "Grand sac"
    quantity = models.IntegerField(help_text="Quantité associée à cette unité (exemple : 10 œufs)")
    price = models.FloatField(help_text="Prix de cette unité")
    discounts = models.ManyToManyField('Discount', blank=True)  # Remises applicables à cette unité

    def apply_discounts(self):
        """Applique toutes les remises à cette unité."""
        discounted_price = self.price
        for discount in self.discounts.all():
            discounted_price = discount.apply_discount(discounted_price)
        return discounted_price

    def __str__(self):
        return f"{self.name} ({self.quantity} unités) - {self.price} €"


class Discount(models.Model):
    """Remises pouvant être appliquées aux unités de produit."""
    name = models.CharField(max_length=100)
    percentage = models.FloatField(help_text="Pourcentage de réduction (exemple : 10 pour 10%)")

    def apply_discount(self, price):
        """Calcule le prix après application de la remise."""
        return price * (1 - self.percentage / 100)

    def __str__(self):
        return f"{self.name} - {self.percentage}%"
