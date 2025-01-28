from django.db import models


class Template(models.Model):
    name = models.CharField(max_length=255, verbose_name="Template Name")
    preview_image = models.ImageField(upload_to='template_previews/', null=True, blank=True, verbose_name="Preview Image")
    file_path = models.FileField(upload_to='templates/', help_text="Base HTML file for the template.")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    def __str__(self):
        return self.name

    def get_template_file(self):
        """Returns the relative path of the associated template file."""
        return self.file_path.name

    class Meta:
        verbose_name = "Template"
        verbose_name_plural = "Templates"


class CompanyProfile(models.Model):
    name = models.CharField(max_length=500, null=True, blank=True, verbose_name="Company Name")
    logo = models.ImageField(upload_to='company_logos/', null=True, blank=True, verbose_name="Logo")
    favicon = models.ImageField(upload_to='company_favicons/', null=True, blank=True, verbose_name="Favicon")
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name="company_profiles", null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True, verbose_name="Address")
    city = models.CharField(max_length=100, null=True, blank=True, verbose_name="City")
    state = models.CharField(max_length=100, null=True, blank=True, verbose_name="State")
    zip_code = models.CharField(max_length=10, null=True, blank=True, verbose_name="ZIP Code")
    country = models.CharField(max_length=100, null=True, blank=True, verbose_name="Country")
    description = models.TextField(null=True, blank=True, verbose_name="Description")
    primary_color = models.CharField(max_length=7, null=True, blank=True, verbose_name="Primary Color")
    secondary_color = models.CharField(max_length=7, null=True, blank=True, verbose_name="Secondary Color")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    def __str__(self):
        return self.name or "Unnamed Company"

    class Meta:
        verbose_name = "Company Profile"
        verbose_name_plural = "Company Profiles"


class PageConfig(models.Model):
    # Hero Section
    hero_image = models.ImageField(upload_to='hero_images/', null=True, blank=True, verbose_name="Hero Image")
    hero_title = models.CharField(max_length=200, null=True, blank=True, verbose_name="Hero Title")
    hero_subtitle = models.CharField(max_length=500, null=True, blank=True, verbose_name="Hero Subtitle")
    hero_button_text = models.CharField(max_length=100, null=True, blank=True, verbose_name="Hero Button Text")
    hero_button_link = models.URLField(null=True, blank=True, verbose_name="Hero Button Link")

    # About Section
    about_title = models.CharField(max_length=200, null=True, blank=True, verbose_name="About Title")
    about_description = models.TextField(null=True, blank=True, verbose_name="About Description")

    # Services Section
    service_title = models.CharField(max_length=200, null=True, blank=True, verbose_name="Service Title")
    service_description = models.TextField(null=True, blank=True, verbose_name="Service Description")
    service_image = models.ImageField(upload_to='service_images/', null=True, blank=True, verbose_name="Service Image")

    # Testimonials Section
    testimonials = models.JSONField(null=True, blank=True, verbose_name="Testimonials")

    # Contact Section
    contact_email = models.EmailField(null=True, blank=True, verbose_name="Contact Email")
    contact_phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Contact Phone")
    contact_address = models.CharField(max_length=500, null=True, blank=True, verbose_name="Contact Address")

    # Footer
    footer_text = models.TextField(null=True, blank=True, verbose_name="Footer Text")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    def __str__(self):
        return f"Page Configuration"

    class Meta:
        verbose_name = "Page Configuration"
        verbose_name_plural = "Page Configurations"


class PaymentIntegration(models.Model):
    """Intégration de paiement pour chaque utilisateur."""
    PROVIDER_CHOICES = [
        ('cinetpay', 'CinetPay'),

    ]

  
    provider = models.CharField(
        max_length=50,
        choices=PROVIDER_CHOICES,
        verbose_name="Fournisseur",
        help_text="Fournisseur de service de paiement."
    )
    site_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Id du Site",
        help_text="Site Id fournie par le fournisseur de paiement."
    )
    api_key = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Clé API",
        help_text="Clé API fournie par le fournisseur de paiement."
    )
    secret_key = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Clé secrète",
        help_text="Clé secrète fournie par le fournisseur de paiement."
    )
    currency = models.CharField(
        max_length=10,
        default="USD",
        verbose_name="Devise",
        help_text="Devise préférée pour les paiements."
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Active ou désactive cette intégration."
    )
    metadata = models.JSONField(
        null=True,
        blank=True,
        verbose_name="Métadonnées",
        help_text="Autres configurations spécifiques au fournisseur."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.provider} - {self.user.username}"

    class Meta:
        verbose_name = "Intégration de paiement"
        verbose_name_plural = "Intégrations de paiement"




class EmailConfig(models.Model):
    email_host = models.CharField(max_length=255, default='smtp.gmail.com', verbose_name="SMTP Host")
    email_port = models.IntegerField(default=587, verbose_name="SMTP Port")
    email_use_tls = models.BooleanField(default=True, verbose_name="Use TLS")
    email_host_user = models.EmailField(max_length=255, verbose_name="SMTP Username (Email)")
    email_host_password = models.CharField(max_length=255, verbose_name="SMTP Password (App Password)")
    default_from_email = models.EmailField(max_length=255, verbose_name="Default From Email")
    
    def __str__(self):
        return f"Email Configuration for {self.email_host_user}"

    class Meta:
        verbose_name = "Email Configuration"
        verbose_name_plural = "Email Configurations"