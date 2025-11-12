"""
Esse arquivo é tipo o mapa do nosso site!
Ele diz pro Django: "quando alguém digitar esse endereço, mostra essa página"

Por exemplo:
- Se digitar "meusite.com/" -> mostra a página inicial
- Se digitar "meusite.com/livros/" -> mostra a lista de livros
- Se digitar "meusite.com/admin/" -> abre o painel de administração

É como um GPS que direciona as pessoas para o lugar certo no site!
"""

from django.contrib import admin
from django.urls import path, include  # 'include' é pra incluir URLs de outros apps
from django.conf import settings  # Configurações do projeto (tipo as preferências)
from django.conf.urls.static import static  # Para servir imagens e arquivos que o usuário vai upar

urlpatterns = [
    # ==========================================
    # PAINEL ADMIN - Onde os administradores gerenciam tudo
    # ==========================================
    # Aqui é tipo o "modo criativo" do Minecraft - só pra quem tem poderes especiais!
    # Acesse: http://localhost:8000/admin/
    path('admin/', admin.site.urls),
    
    
    # ==========================================
    # TODAS AS PÁGINAS DO APP DE LEITURA
    # ==========================================
    # Aqui a gente "importa" todas as rotas que criamos no arquivo urls.py do nosso app
    # É tipo dizer: "tudo que começar com nada (''), usa as URLs que tão lá em nomeapp/urls.py"
    # Então se lá tem 'livros/', aqui vai virar '/livros/'
    path('', include('nomeapp.urls')),
    
    
    # ==========================================
    # AUTENTICAÇÃO - Login, Logout, Cadastro
    # ==========================================
    # O Django já vem com um sistema pronto de login! É só usar!
    # Acesse: http://localhost:8000/accounts/login/ para fazer login
    # Acesse: http://localhost:8000/accounts/logout/ para sair
    path('accounts/', include('django.contrib.auth.urls')),
]

# ==========================================
# CONFIGURAÇÃO PARA SERVIR IMAGENS E ARQUIVOS
# ==========================================
# Isso aqui é SUPER IMPORTANTE quando estamos testando localmente (DEBUG=True)
# Permite que o Django mostre as imagens que o usuário fez upload (capas de livros, fotos, etc)
# Em produção (site real na internet), isso é feito de forma diferente
if settings.DEBUG:
    # Se estamos em modo de desenvolvimento (testando no computador)...
    # Serve os arquivos de mídia (imagens, PDFs, etc) que os usuários fazem upload
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Serve os arquivos estáticos (CSS, JavaScript, imagens do site)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

