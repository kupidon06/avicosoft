from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.conf import settings
from .models import Fournisseur,EmployeeProfile,User
from .forms import FournisseurForm,EmployeeProfileForm,UserForm
from openpyxl import Workbook
import json
import os
from django.core.paginator import Paginator
from .decorators import role_required

login_path = '/accounts/login'


@login_required(login_url='login')
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def user_list(request):
    query = request.GET.get('q')
    if query:
        users = User.objects.filter(Q(name__icontains=query) | Q(email__icontains=query)).distinct().order_by('id')
    else:
        users = User.objects.all().order_by('id')

    paginator = Paginator(users, 10)  # Afficher 10 utilisateurs par page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = UserForm()

    context = {
        'users': page_obj,
        'form': form,
    }

    return render(request, 'apps/users/list.html', context)


@login_required(login_url='login')
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def delete_user(request, id):
    user = get_object_or_404(User, id=id)
    user.delete()
    return redirect('user_list')


@login_required(login_url='login')
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def update_user(request, id):
    user = get_object_or_404(User, id=id)

    if request.method == "POST":
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.role = request.POST.get('role', user.role)
        user.is_active  = request.POST.get('is_active', user.is_active)
        user.save()
        return redirect('user_list')

    
    


@csrf_exempt
@login_required(login_url='login')
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def bulk_delete_users(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_ids = data.get('user_ids', [])
            action = data.get('action', 'delete')

            if not user_ids:
                return JsonResponse({'status': 'error', 'message': 'Aucun utilisateur sélectionné.'}, status=400)

            if action == 'delete':
                users = User.objects.filter(id__in=user_ids)
                users_deleted, _ = users.delete()
                return JsonResponse({'status': 'success', 'message': f'{users_deleted} utilisateur(s) supprimé(s).'})

            elif action == 'activate':
                users = User.objects.filter(id__in=user_ids)
                users.update(is_active=True)
                return JsonResponse({'status': 'success', 'message': f'{users.count()} utilisateur(s) activé(s).'})

            else:
                return JsonResponse({'status': 'error', 'message': 'Action non reconnue.'}, status=400)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée.'}, status=405)



@login_required(login_url=login_path)
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def employee_profile_list(request):
    query = request.GET.get('q')
    if query:
        employee_profiles = EmployeeProfile.objects.filter(Q(user__username__icontains=query)| Q(user__email__icontains=query)).distinct().order_by('id')
    else:
        employee_profiles = EmployeeProfile.objects.all().order_by('id')

    paginator = Paginator(employee_profiles, 10)  # Show 10 employee profiles per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        form = EmployeeProfileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('employee_profile_list')
    else:
        form = EmployeeProfileForm()

    context = {
        'employee_profiles': page_obj,
        'form': form,
    }

    return render(request, 'apps/employee_profiles/list.html', context)

@login_required(login_url=login_path)
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def employee_profile_list_print(request):
    query = request.GET.get('q')
    if query:
        employee_profiles = EmployeeProfile.objects.filter(Q(user__name__icontains=query)).distinct().order_by('id')
    else:
        employee_profiles = EmployeeProfile.objects.all().order_by('id')

    context = {
        'employee_profiles': employee_profiles,
    }

    return render(request, 'apps/employee_profiles/list_print.html', context)

@login_required(login_url=login_path)
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def employee_profile_list_export(request):
    query = request.GET.get('q')
    if query:
        employee_profiles = EmployeeProfile.objects.filter(Q(user__name__icontains=query)).distinct().order_by('id')
    else:
        employee_profiles = EmployeeProfile.objects.all().order_by('id')

    # Créer un nouveau classeur
    wb = Workbook()
    ws = wb.active
    ws.title = "Employee Profiles"

    # Ajouter les en-têtes
    ws.append(["ID", "Name", "Position", "Salary", "Identity"])

    # Ajouter les données des employés
    for employee_profile in employee_profiles:
        ws.append([employee_profile.id, employee_profile.user.name, employee_profile.position, employee_profile.salary, employee_profile.identity.url if employee_profile.identity else ""])

    # Créer une réponse HTTP avec le fichier Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=employee_profiles.xlsx'

    # Enregistrer le classeur dans la réponse
    wb.save(response)

    return response

@csrf_exempt
@login_required(login_url=login_path)
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def update_employee_profile(request, id):
    employee_profile = get_object_or_404(EmployeeProfile, id=id)

    if request.method == "POST":
        form = EmployeeProfileForm(request.POST, request.FILES, instance=employee_profile)
        if form.is_valid():
            form.save()
            return redirect('employee_profile_list')
    else:
        form = EmployeeProfileForm(instance=employee_profile)

    context = {
        'form': form,
    }

    return render(request, 'apps/employee_profiles/update_employee_profile.html', context)

@csrf_exempt
@login_required(login_url=login_path)
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def delete_employee_profile(request, id):
    employee_profile = get_object_or_404(EmployeeProfile, id=id)
    employee_profile.delete()
    return redirect('employee_profile_list')

@csrf_exempt
@login_required(login_url=login_path)
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def bulk_delete_employee_profile(request):
    if request.method == 'POST':
        try:
            # Récupérer les données JSON envoyées
            data = json.loads(request.body)
            employee_profile_ids = data.get('employee_profile_ids', [])
            action = data.get('action', 'delete')  # Action à effectuer: 'toggle' ou 'delete'

            if not employee_profile_ids:
                return JsonResponse({'status': 'error', 'message': 'Aucun employé sélectionné.'}, status=400)

            elif action == 'delete':
                # Supprimer les employés
                employee_profiles = EmployeeProfile.objects.filter(id__in=employee_profile_ids)
                employee_profiles_deleted, _ = employee_profiles.delete()

                return JsonResponse({'status': 'success', 'message': f'{employee_profiles_deleted} employé(s) supprimé(s).'})

            else:
                return JsonResponse({'status': 'error', 'message': 'Action non reconnue.'}, status=400)

        except Exception as e:
            # Renvoie une erreur avec un message détaillé
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée.'}, status=405)


@login_required(login_url=login_path)
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def fournisseur_list(request):
    query = request.GET.get('q')
    if query:
        fournisseurs = Fournisseur.objects.filter(Q(name__icontains=query)).distinct().order_by('id')
    else:
        fournisseurs = Fournisseur.objects.all().order_by('id')

    paginator = Paginator(fournisseurs, 10)  # Show 10 fournisseurs per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        form = FournisseurForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('fournisseur_list')
    else:
        form = FournisseurForm()

    context = {
        'fournisseurs': page_obj,
        'form': form,
    }

    return render(request, 'apps/fournisseurs/list.html', context)

@login_required(login_url=login_path)
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def fournisseur_list_print(request):
    query = request.GET.get('q')
    if query:
        fournisseurs = Fournisseur.objects.filter(Q(name__icontains=query)).distinct().order_by('id')
    else:
        fournisseurs = Fournisseur.objects.all().order_by('id')

    context = {
        'fournisseurs': fournisseurs,
    }

    return render(request, 'apps/fournisseurs/list_print.html', context)

@login_required(login_url=login_path)
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def fournisseur_list_export(request):
    query = request.GET.get('q')
    if query:
        fournisseurs = Fournisseur.objects.filter(Q(name__icontains=query)).distinct().order_by('id')
    else:
        fournisseurs = Fournisseur.objects.all().order_by('id')

    # Créer un nouveau classeur
    wb = Workbook()
    ws = wb.active
    ws.title = "Fournisseurs"

    # Ajouter les en-têtes
    ws.append(["ID", "Name", "Phone", "Address", "Details"])

    # Ajouter les données des fournisseurs
    for fournisseur in fournisseurs:
        ws.append([fornisseur.id, fournisseur.name, fournisseur.phone, fournisseur.address, fournisseur.details])

    # Créer une réponse HTTP avec le fichier Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=fournisseurs.xlsx'

    # Enregistrer le classeur dans la réponse
    wb.save(response)

    return response

@csrf_exempt
@login_required(login_url=login_path)
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def update_fournisseur(request, id):
    fournisseur = get_object_or_404(Fournisseur, id=id)

    if request.method == "POST":
        form = FournisseurForm(request.POST, instance=fournisseur)
        if form.is_valid():
            form.save()
            return redirect('fournisseur_list')
    else:
        form = FournisseurForm(instance=fournisseur)

    context = {
        'form': form,
    }

    return render(request, 'apps/fournisseurs/update_fournisseur.html', context)

@csrf_exempt
@login_required(login_url=login_path)
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def delete_fournisseur(request, id):
    fournisseur = get_object_or_404(Fournisseur, id=id)
    fournisseur.delete()
    return redirect('fournisseur_list')

@csrf_exempt
@login_required(login_url=login_path)
@role_required(excluded_roles=['customer','cashier','veterinarian','accountant','employee','farmer']) 
def bulk_delete_fournisseur(request):
    if request.method == 'POST':
        try:
            # Récupérer les données JSON envoyées
            data = json.loads(request.body)
            fournisseur_ids = data.get('fournisseur_ids', [])
            action = data.get('action', 'delete')  # Action à effectuer: 'toggle' ou 'delete'

            if not fournisseur_ids:
                return JsonResponse({'status': 'error', 'message': 'Aucun fournisseur sélectionné.'}, status=400)

            elif action == 'delete':
                # Supprimer les fournisseurs
                fournisseurs = Fournisseur.objects.filter(id__in=fournisseur_ids)
                fournisseurs_deleted, _ = fournisseurs.delete()

                return JsonResponse({'status': 'success', 'message': f'{fournisseurs_deleted} fournisseur(s) supprimé(s).'})

            else:
                return JsonResponse({'status': 'error', 'message': 'Action non reconnue.'}, status=400)

        except Exception as e:
            # Renvoie une erreur avec un message détaillé
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée.'}, status=405)
