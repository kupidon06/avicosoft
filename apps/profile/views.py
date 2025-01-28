from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Template, CompanyProfile, PageConfig,PaymentIntegration
from .forms import TemplateForm, CompanyProfileForm, PageConfigForm,PaymentIntegrationForm
import json
from django.http import JsonResponse
from apps.users.decorators import role_required




@login_required(login_url='login')
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def template_list(request):
    query = request.GET.get('q')
    templates = Template.objects.filter(name__icontains=query) if query else Template.objects.all()

    paginator = Paginator(templates, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Formulaire de création
    if request.method == 'POST':
        form = TemplateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Le modèle a été créé avec succès.")
            return redirect('template_list')
        else:
            messages.error(request, "Erreur dans les données du formulaire.")
    else:
        form = TemplateForm()

    return render(request, 'apps/templates/list.html', {'templates': page_obj, 'form': form})


@login_required(login_url='login')
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def template_list_print(request):
    query = request.GET.get('q')
    templates = Template.objects.filter(name__icontains=query) if query else Template.objects.all()
    return render(request, 'apps/templates/list_print.html', {'templates': templates})


@login_required(login_url='login')
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def template_list_export(request):
    query = request.GET.get('q')
    templates = Template.objects.filter(name__icontains=query) if query else Template.objects.all()

    wb = Workbook()
    ws = wb.active
    ws.title = "Templates"
    ws.append(["ID", "Name", "File Path", "Preview Image", "Created At"])

    for template in templates:
        ws.append([template.id, template.name, template.get_template_file(), template.preview_image.url if template.preview_image else '', template.created_at])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=templates.xlsx'
    wb.save(response)

    return response


@login_required(login_url='login')
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def update_template(request, id):
    template = get_object_or_404(Template, id=id)
    if request.method == "POST":
        form = TemplateForm(request.POST, request.FILES, instance=template)
        if form.is_valid():
            form.save()
            messages.success(request, "Le modèle a été mis à jour avec succès.")
            return redirect('template_list')
        else:
            messages.error(request, "Erreur dans les données du formulaire.")
    else:
        form = TemplateForm(instance=template)

    return render(request, 'apps/templates/update.html', {'form': form, 'template': template})


@login_required(login_url='login')
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def delete_template(request, id):
    template = get_object_or_404(Template, id=id)
    template.delete()
    messages.success(request, "Le modèle a été supprimé avec succès.")
    return redirect('template_list')


@login_required(login_url='login')
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def bulk_delete_templates(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            template_ids = data.get('template_ids', [])

            if not template_ids:
                return JsonResponse({'status': 'error', 'message': 'Aucun modèle sélectionné.'}, status=400)

            templates_deleted, _ = Template.objects.filter(id__in=template_ids).delete()
            return JsonResponse({'status': 'success', 'message': f'{templates_deleted} modèle(s) supprimé(s).'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée.'}, status=405)

### Gestion des Profils de Compagnie (1 seul par utilisateur)

@login_required(login_url='login')
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def company_profile_list(request):
    profile = CompanyProfile.objects.first()
      # On considère qu'il n'y a qu'un seul profil global
    templates = Template.objects.all()

    exemple=PageConfig.objects.first() 
    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, request.FILES)
        config = PageConfigForm(request.POST, request.FILES)
        if form.is_valid() :
            company = form.save()
            return redirect('company_profile_list')
        else:
            messages.error(request, "Erreur dans les données du formulaire.")
        if config.is_valid() :
            config.save()
            return redirect('company_profile_list')
        else:
            messages.error(request, "Erreur dans les données du formulaire.")
    else:
        form = CompanyProfileForm()
        config = PageConfigForm()
    return render(request, 'apps/company_profiles/list.html', {'form': form,'config':config, 'profile':profile,'pageconfig':exemple,'templates':templates})


@login_required(login_url='login')
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def update_company_profile(request, id):
    profile = get_object_or_404(CompanyProfile, id=id)
    if request.method == "POST":
        form = CompanyProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Le profil de la compagnie a été mis à jour avec succès.")
            return redirect('company_profile_list')
        else:
            messages.error(request, "Erreur dans les données du formulaire.")
    else:
        form = CompanyProfileForm(instance=profile)

    return render(request, 'apps/company_profiles/update.html', {'form': form, 'profile': profile})


@login_required(login_url='login')
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def delete_company_profile(request, id):
    profile = get_object_or_404(CompanyProfile, id=id)
    profile.delete()
    messages.success(request, "Le profil de la compagnie a été supprimé avec succès.")
    return redirect('company_profile_list')


### Gestion des Configurations de Page (1 seule par utilisateur)

@login_required(login_url='login')
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def page_config_list(request):
   

    if request.method == 'POST':
        print("salut")
        form = PageConfigForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "La configuration de la page a été créée avec succès.")
            return redirect('company_profile_list')
        else:
            messages.error(request, "Erreur dans les données du formulaire.")
    else:
        form = PageConfigForm()

    return render(request, 'apps/page_configs/create.html', {'form': form})


@login_required(login_url='login')
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def update_page_config(request, id):
    page_config = get_object_or_404(PageConfig, id=id)
    if request.method == "POST":
        form = PageConfigForm(request.POST, request.FILES, instance=page_config)
        if form.is_valid():
            form.save()
            messages.success(request, "La configuration de la page a été mise à jour avec succès.")
            return redirect('page_config_list')
        else:
            messages.error(request, "Erreur dans les données du formulaire.")
    else:
        form = PageConfigForm(instance=page_config)

    return render(request, 'apps/page_configs/update.html', {'form': form, 'page_config': page_config})


@login_required(login_url='login')
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def delete_page_config(request, id):
    page_config = get_object_or_404(PageConfig, id=id)
    page_config.delete()
    messages.success(request, "La configuration de la page a été supprimée avec succès.")
    return redirect('page_config_list')


from .models import CompanyProfile, PaymentIntegration, EmailConfig
from .forms import CompanyProfileForm, PaymentIntegrationForm, EmailConfigForm  # Assurez-vous de créer ce formulaire
@login_required(login_url='login')
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def profile_settings(request):
    # Charger ou créer les instances
    profile = CompanyProfile.objects.first() or CompanyProfile()
    integration = PaymentIntegration.objects.first() or PaymentIntegration()
    email_config = EmailConfig.objects.first() or EmailConfig()

    # Initialiser les formulaires
    profile_form = CompanyProfileForm(request.POST or None, request.FILES or None, instance=profile, prefix="profile")
    payment_form = PaymentIntegrationForm(request.POST or None, instance=integration, prefix="payment")
    email_form = EmailConfigForm(request.POST or None, instance=email_config, prefix="email")

    # Gestion des envois individuels
    if request.method == "POST":
        if "profile_submit" in request.POST and profile_form.is_valid():
            profile_form.save()
            return redirect("company_profile_list")
        elif "payment_submit" in request.POST and payment_form.is_valid():
            payment_form.save()
            return redirect("company_profile_list")
        elif "email_submit" in request.POST and email_form.is_valid():
            email_form.save()
            return redirect("company_profile_list")

    return render(
        request,
        "pages/profile_settings.html",
        {
            "profile_form": profile_form,
            "payment_form": payment_form,
            "email_form": email_form,
        },
    )