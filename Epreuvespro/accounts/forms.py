from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from django.core.exceptions import ValidationError
import re



class CustomUserCreationForm(UserCreationForm):
    """Formulaire d'inscription personnalisé"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'votre@email.com'
        })
    )
    
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Jean'
        }),
        label="Prénom"
    )
    
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Dupont'
        }),
        label="Nom"
    )
    
    telephone = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '+229 XX XX XX XX'
        }),
        label="Téléphone"
    )
    
    classe = forms.ChoiceField(
        choices=CustomUser.CLASSE_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-input'
        }),
        label="Classe"
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••',
            'id': 'register-password'
        }),
        label="Mot de passe"
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••',
            'id': 'confirm-password'
        }),
        label="Confirmer le mot de passe"
    )
    
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'telephone', 'classe', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']  # Utilise l'email comme username
        if commit:
            user.save()
        return user
    




    def clean_password1(self):
        """Validation personnalisée du mot de passe"""
        password = self.cleaned_data.get('password1')
        
        if len(password) < 8:
            raise ValidationError("Le mot de passe doit contenir au moins 8 caractères.")
        
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Le mot de passe doit contenir au moins une lettre majuscule.")
        
        if not re.search(r'[a-z]', password):
            raise ValidationError("Le mot de passe doit contenir au moins une lettre minuscule.")
        
        if not re.search(r'[0-9]', password):
            raise ValidationError("Le mot de passe doit contenir au moins un chiffre.")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("Le mot de passe doit contenir au moins un caractère spécial (!@#$%^&*).")
        
        return password
    
    def clean_email(self):
        """Vérifie que l'email n'est pas déjà utilisé"""
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Cet email est déjà utilisé.")
        return email
    


class CustomAuthenticationForm(AuthenticationForm):
    """Formulaire de connexion personnalisé"""
    
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'votre@email.com'
        }),
        label="Email"
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': '••••••••',
            'id': 'login-password'
        }),
        label="Mot de passe"
    )


class UserProfileForm(forms.ModelForm):
    """Formulaire de modification du profil"""
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'telephone', 'classe', 'photo']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'telephone': forms.TextInput(attrs={'class': 'form-input'}),
            'classe': forms.Select(attrs={'class': 'form-input'}),
            'photo': forms.FileInput(attrs={'class': 'form-input'}),
        }









