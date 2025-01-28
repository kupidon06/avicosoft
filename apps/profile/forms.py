from django import forms
from .models import Template,  EmailConfig, CompanyProfile, PageConfig, PaymentIntegration

class TemplateForm(forms.ModelForm):
    class Meta:
        model = Template
        fields = ['name', 'preview_image', 'file_path']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block w-full p-2.5',
                'placeholder': 'Template Name',
            }),
            'preview_image': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50',
            }),
            'file_path': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50',
            }),
        }

class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = [
            'name', 'logo', 'favicon', 'template', 'address', 'city', 'state',
            'zip_code', 'country', 'description', 'primary_color', 'secondary_color'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block w-full p-2.5',
                'placeholder': 'Company Name',
            }),
            'logo': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50',
            }),
            'favicon': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50',
            }),
            'template': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5',
            }),
            'address': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5',
                'placeholder': 'Address',
            }),
            'city': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5',
                'placeholder': 'City',
            }),
            'state': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5',
                'placeholder': 'State',
            }),
            'zip_code': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5',
                'placeholder': 'ZIP Code',
            }),
            'country': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5',
                'placeholder': 'Country',
            }),
            'description': forms.Textarea(attrs={
                'class': 'block w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 4,
                'placeholder': 'Description',
            }),
            'primary_color': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5',
                'placeholder': '#Primary Color',
            }),
            'secondary_color': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5',
                'placeholder': '#Secondary Color',
            }),
        }

class PageConfigForm(forms.ModelForm):
    class Meta:
        model = PageConfig
        fields = [
            'hero_image', 'hero_title', 'hero_subtitle', 'hero_button_text', 'hero_button_link',
            'about_title', 'about_description',
            'service_title', 'service_description', 'service_image',
            'testimonials', 'contact_email', 'contact_phone', 'contact_address', 'footer_text'
        ]
        widgets = {
            'hero_image': forms.ClearableFileInput(attrs={
                'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50',
            }),
            'hero_title': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block w-full p-2.5',
                'placeholder': 'Hero Title',
            }),
            'hero_subtitle': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block w-full p-2.5',
                'placeholder': 'Hero Subtitle',
            }),
            'hero_button_text': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block w-full p-2.5',
                'placeholder': 'Button Text',
            }),
            'hero_button_link': forms.URLInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block w-full p-2.5',
                'placeholder': 'Button Link',
            }),
            'about_title': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5',
                'placeholder': 'About Title',
            }),
            'about_description': forms.Textarea(attrs={
                'class': 'block w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 4,
                'placeholder': 'About Description',
            }),
            'service_title': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5',
                'placeholder': 'Service Title',
            }),
            'service_description': forms.Textarea(attrs={
                'class': 'block w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 4,
                'placeholder': 'Service Description',
            }),
            'testimonials': forms.Textarea(attrs={
                'class': 'block w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 4,
                'placeholder': 'Testimonials (JSON format)',
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5',
                'placeholder': 'Email',
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5',
                'placeholder': 'Phone',
            }),
            'contact_address': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5',
                'placeholder': 'Address',
            }),
            'footer_text': forms.Textarea(attrs={
                'class': 'block w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 2,
                'placeholder': 'Footer Text',
            }),
        }

class PaymentIntegrationForm(forms.ModelForm):
    class Meta:
        model = PaymentIntegration
        fields = [
            'provider','site_id', 'api_key', 'secret_key',
            'currency', 'is_active','metadata'
        ]
        widgets = {
            'provider': forms.Select(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5',
            }),
            'site_id': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5',
                'placeholder': 'API Key',
            }),
            'api_key': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5',
                'placeholder': 'API Key',
            }),
            'secret_key': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5',
                'placeholder': 'API Secret',
            }),
            'currency': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5',
                'placeholder': 'API URL',
            }),
           
            'metadata': forms.Textarea(attrs={
                'class': 'block w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-indigo-500 focus:border-indigo-500',
                'rows': 4,
                'placeholder': 'Additional Config (JSON format)',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded',
            }),
        }


class EmailConfigForm(forms.ModelForm):
    class Meta:
        model = EmailConfig
        fields = [
            'email_host', 'email_port', 'email_use_tls', 'email_host_user',
            'email_host_password', 'default_from_email'
        ]
        widgets = {
            'email_host': forms.TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5',
                'placeholder': 'SMTP Host (e.g., smtp.gmail.com)',
            }),
            'email_port': forms.NumberInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5',
                'placeholder': 'SMTP Port (e.g., 587)',
            }),
            'email_use_tls': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded',
            }),
            'email_host_user': forms.EmailInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5',
                'placeholder': 'SMTP Username (Email)',
            }),
            'email_host_password': forms.PasswordInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5',
                'placeholder': 'SMTP Password (App Password)',
            }),
            'default_from_email': forms.EmailInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg block w-full p-2.5',
                'placeholder': 'Default From Email',
            }),
        }