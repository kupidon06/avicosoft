from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Template, CompanyProfile, PageConfig

from django.template import Template, Context
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

def render_page(request, template_id):
    # Récupérer le modèle Template
    company_profile = CompanyProfile.objects.first()
    template_obj=company_profile.template
    # Récupérer le fichier HTML uploadé
    try:
        with open(template_obj.file_path.path, 'r', encoding='utf-8') as template_file:
            template_content = template_file.read()
    except FileNotFoundError:
        return HttpResponse("Template file not found.", status=404)

    # Charger le contenu du fichier comme un Template
    compiled_template = Template(template_content)

    # Préparer le contexte
    
    page_config = PageConfig.objects.filter().first()

    context = {
        'company_profile': company_profile,
        'page_config': page_config,
    }

    # Rendre le template avec le contexte
    rendered_content = compiled_template.render(Context(context))

    # Retourner une réponse HTTP avec le contenu rendu
    return HttpResponse(rendered_content)
