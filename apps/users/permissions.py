from rest_framework import permissions
from rest_framework.permissions import BasePermission

class IsSuperUserOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return request.user and request.user.is_superuser

class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Les utilisateurs staff ont un accès complet, les autres utilisateurs ont un accès en lecture seule.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée pour permettre uniquement au propriétaire de l'objet de modifier ou supprimer.
    Les superutilisateurs ont un accès complet.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_superuser:
            return True
        return obj.user == request.user

class IsSelfOrReadOnly(permissions.BasePermission):
    """
    Permission personnalisée pour permettre aux utilisateurs de voir et éditer leur propre profil uniquement.
    Les superutilisateurs peuvent voir et éditer tous les profils.
    """

    def has_permission(self, request, view):
        # Autorise l'accès en lecture pour tous
        if request.method in permissions.SAFE_METHODS:
            return True
        # Autorise la création d'un nouveau profil utilisateur par les non-authentifiés ou les superutilisateurs
        if view.action == 'create':
            return not request.user.is_authenticated or request.user.is_superuser
        # Pour les autres méthodes, l'utilisateur doit être authentifié
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Les superutilisateurs peuvent tout faire
        if request.user.is_superuser:
            return True
        # Les utilisateurs peuvent voir et modifier leur propre profil
        return obj == request.user