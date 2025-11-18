"""
Arquivo de FORMULÁRIOS
VAMOS UTILIZAR formularios prontos do django e personaliza los
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

# Pega o modelo de usuário que estamos usando (o nosso Usuario personalizado)
User = get_user_model()


class SignUpForm(UserCreationForm):
    """
    Formulário de Cadastro (Sign Up)
    
    Herda do UserCreationForm do Django (que já vem pronto com username e senha)
    e adiciona mais campos: email e nome_completo
    """
    
    # Campo de email - OBRIGATÓRIO e Unico
    email = forms.EmailField(
        required=True,  #  não pode deixar vazio
        label="Email",  # O texto que aparece no campo
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',  # Classes do framework Bootstrap pra ficar bonito
            'placeholder': 'seu@email.com',  
        })
    )
    
    # Campo de nome completo - OPCIONAL (pode deixar em branco)
    nome_completo = forms.CharField(
        required=False,  # Não é obrigatório
        max_length=200,  # Máximo 200 caracteres
        label="Nome Completo",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'João da Silva',
        })
    )
    
    class Meta:
        # Qual modelo (tabela do banco de dados) esse formulário usa?
        model = User
        
        # ordem dos campos do formulario
        fields = ('username', 'email', 'nome_completo', 'password1', 'password2')
        
        # Personalizando a aparência dos campos
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'adicione um username',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        """
        QUando o formulário é criado.
        adicionando as classes do framework Bootstrap nos campos de senha
        (que vêm do UserCreationForm)
        """
        super().__init__(*args, **kwargs) 
        
        # Adiciona classes Bootstrap nos campos de senha
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': '********',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': '********',
        })
    
    def clean_email(self):
       # validação do email.
        
        
        email = self.cleaned_data.get('email')
        
        # Verifica se já texiste esse email
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                'Esse email já está em Uso! Faça seu login ou use outro email.'
            )
        
        return email
    
    def save(self, commit=True):
        
        # Função que salva o usuário no banco de dados.
        
        
        # Cria o usuário(INSTANCIA) mas ainda não salva NO base de dados
        user = super().save(commit=False)
        
        # Adiciona o email
        user.email = self.cleaned_data['email']
        
        # Adiciona o nome completo,caso ele tenha preenchido    
        if self.cleaned_data.get('nome_completo'):
            user.nome_completo = self.cleaned_data['nome_completo']
        
        # Agora sim, salva no banco de dados
        if commit:
            user.save()
        
        return user


from .models import Livro, Escritor, Editora

class LivroForm(forms.ModelForm):
    """Formulário para criar/editar livros"""
    class Meta:
        model = Livro
        fields = ['titulo', 'escritor', 'editora', 'ano_publicacao', 'numero_paginas', 'sinopse', 'isbn', 'capa']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título do livro'}),
            'escritor': forms.Select(attrs={'class': 'form-select'}),
            'editora': forms.Select(attrs={'class': 'form-select'}),
            'ano_publicacao': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '2024'}),
            'numero_paginas': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '300'}),
            'sinopse': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Sinopse do livro...'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ISBN'}),
            'capa': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'titulo': 'Título',
            'escritor': 'Escritor(a)',
            'editora': 'Editora',
            'ano_publicacao': 'Ano de Publicação',
            'numero_paginas': 'Número de Páginas',
            'sinopse': 'Sinopse',
            'isbn': 'ISBN',
            'capa': 'Capa do Livro',
        }


class EscritorForm(forms.ModelForm):
    """Formulário para criar/editar escritores"""
    class Meta:
        model = Escritor
        fields = ['nome', 'email', 'bibliografia', 'foto']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@escritor.com'}),
            'bibliografia': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Biografia do escritor...'}),
            'foto': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nome': 'Nome',
            'email': 'E-mail',
            'bibliografia': 'Biografia',
            'foto': 'Foto',
        }


class EditoraForm(forms.ModelForm):
    """Formulário para criar/editar editoras"""
    class Meta:
        model = Editora
        fields = ['nome', 'site', 'telefone']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da editora'}),
            'site': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.editora.com.br'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 98765-4321'}),
        }
        labels = {
            'nome': 'Nome',
            'site': 'Site',
            'telefone': 'Telefone',
        }
