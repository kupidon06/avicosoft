from datetime import timedelta

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_str,force_bytes
from django.conf import settings
from django.core.mail import send_mail
from django.utils.timezone import now
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from .models import User, EmployeeProfile, Fournisseur, Absence
from .serializers import (
    CustomRegisterSerializer, UserSerializer, EmployeeProfileSerializer,
    FournisseurSerializer, AbsenceSerializer, PasswordResetSerializer, ForgotPasswordInputSerializer
)
from .permissions import (
    IsSuperUserOrReadOnly, IsStaffOrReadOnly, IsOwnerOrReadOnly,
    IsSelfOrReadOnly
)
from .filters import (
    UserFilter, EmployeeProfileFilter, FournisseurFilter,
    AbsenceFilter
)



signer = TimestampSigner()

class CustomPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50

class ResendConfirmationEmailView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(
        request=ForgotPasswordInputSerializer,
        responses={200: 'Email envoyé avec succès.', 400: 'Erreur.'},
    )
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email non fourni.'}, status=400)

        try:
            user = User.objects.get(email=email)
            if user.is_active:
                return Response({'message': 'Cet utilisateur est déjà actif.'}, status=400)

            token = signer.sign(user.email)
            confirmation_link = reverse('confirm_email', args=[token])
            full_link = f"{settings.SITE_URL}{confirmation_link}"

            send_mail(
                subject="Confirmation de votre adresse email",
                message=f"Bonjour {user.name},\n\nVoici votre lien de confirmation : {full_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
            return Response({'message': 'Email de confirmation envoyé avec succès.'})
        except User.DoesNotExist:
            return Response({'error': "Utilisateur introuvable avec cet email."}, status=404)

class ForgotPasswordView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(
        request=ForgotPasswordInputSerializer,
        responses={200: 'Email envoyé avec succès.', 400: 'Erreur.'},
    )
    def post(self, request):
        serializer = ForgotPasswordInputSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                
                # Génération du token
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                # Définir l'expiration du lien (par exemple 15 minutes)
                expiration_time = now() + timedelta(minutes=15)

                # Sauvegarder l'expiration du lien avec le token si vous créez un modèle pour le faire.
                # Vous pouvez par exemple sauvegarder cette information dans un modèle PasswordResetToken

                reset_link = reverse('password_reset_view', args=[uid, token])
                full_link = f"{settings.SITE_URL}{reset_link}?expires_at={expiration_time.isoformat()}"

                send_mail(
                    subject="Réinitialisation de votre mot de passe",
                    message=f"Bonjour {user.name},\n\nVoici votre lien de réinitialisation : {full_link}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                )
                return Response({'message': 'Email de réinitialisation envoyé avec succès.'})
            except User.DoesNotExist:
                return Response({'error': "Utilisateur introuvable avec cet email."}, status=404)
        return Response(serializer.errors, status=400)


def reset_password_view(request, uidb64, token):
    return render(request, 'accounts/reset-password.html', {'uid': uidb64, 'token': token})

class PasswordResetConfirmView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(
        request=PasswordResetSerializer,
        responses={200: 'Mot de passe réinitialisé avec succès.', 400: 'Erreur.'},
    )
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if not default_token_generator.check_token(user, token):
                return Response({'error': 'Lien invalide ou expiré.'}, status=400)

            serializer = PasswordResetSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=user)
                return Response({'message': 'Mot de passe réinitialisé avec succès.'})
            return Response(serializer.errors, status=400)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Utilisateur invalide.'}, status=400)

def confirm_email(request, token):
    try:
        email = signer.unsign(token, max_age=3600)
        user = get_object_or_404(User, email=email)
        if not user.is_active:
            user.is_active = True
            user.save()
            return HttpResponse("Votre adresse email a été confirmée avec succès !")
        return HttpResponse("Votre adresse email est déjà confirmée.")
    except SignatureExpired:
        return HttpResponseBadRequest("Ce lien de confirmation a expiré.")
    except BadSignature:
        return HttpResponseBadRequest("Lien de confirmation invalide.")

class CustomRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = CustomRegisterSerializer

    def perform_create(self, serializer):
        serializer.save(request=self.request)


class SelfOnlyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSelfOrReadOnly]

    def get_queryset(self):
        # Filtrer les résultats pour que les utilisateurs ne voient que leurs propres données
        if self.request.user.role == 'employee':
            return self.queryset.all()
        return self.queryset.filter(id=self.request.user.id)

class UserViewSet(SelfOnlyViewSet):
    queryset = User.objects.all().order_by('id')  # Trié par ID, vous pouvez ajuster cela selon vos besoins
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,IsSelfOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = UserFilter
    

class EmployeeProfileViewSet(viewsets.ModelViewSet):
    queryset = EmployeeProfile.objects.all()
    serializer_class = EmployeeProfileSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = EmployeeProfileFilter
    pagination_class = CustomPagination

class FournisseurViewSet(viewsets.ModelViewSet):
    queryset = Fournisseur.objects.all()
    serializer_class = FournisseurSerializer
    permission_classes = (IsAuthenticated, IsStaffOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FournisseurFilter
    pagination_class = CustomPagination

class AbsenceViewSet(viewsets.ModelViewSet):
    queryset = Absence.objects.all()
    serializer_class = AbsenceSerializer
    permission_classes = (IsAuthenticated, IsSuperUserOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AbsenceFilter
    pagination_class = CustomPagination
