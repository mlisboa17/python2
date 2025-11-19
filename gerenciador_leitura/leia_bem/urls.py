from django.urls import path
from . import views

urlpatterns = [
    # ==========================================
    # PÁGINAS PÚBLICAS - Qualquer pessoa pode acessar
    # ==========================================
    
    # Página inicial do site
    path('', views.index, name='index'),
    
    # Página de login customizada
    path('login/', views.CustomLoginView.as_view(), name='login'),
    
    # Página de cadastro - cria uma nova conta
    path('cadastro/', views.signup, name='signup'),
    
    # Lista completa de livros disponíveis - mostra todos os livros no sistema
    path('livros/', views.lista_livros, name='lista_livros'),
    
    # Página de detalhes de um livro específico - mostra informações completas e avaliações
    # Exemplo: livros/5/ mostra os detalhes do livro com ID 5
    path('livros/<int:livro_id>/', views.detalhe_livro, name='detalhe_livro'),
    
    
    # A´rea do usuario Apenas usuários logados podem acessar
    
    # Minha biblioteca pessoal - mostra todos os livros que estou lendo
    path('meus-livros/', views.meus_livros, name='meus_livros'),
    
    # Adicionar um livro a minha biblioteca
    path('livros/<int:livro_id>/adicionar/', views.adicionar_livro_leitura, name='adicionar_livro_leitura'),

    
   
    
    # Atualizar quantas páginas foram lidas 
    path('progresso/<int:progresso_id>/atualizar/', views.atualizar_progresso, name='atualizar_progresso'),
    
    # Registrar que fiz uma sessão de leitura hoje - ganha pontos!
    # Quanto mais dias seguidos você ler, mais pontos você ganha
    path('progresso/<int:progresso_id>/sessao/', views.registrar_sessao_leitura, name='registrar_sessao'),
    
    
    # ==========================================
    # AVALIAÇÕES - Dar notas e comentários sobre os livros
    # ==========================================
    
    # Avaliar um livro com nota de 1 a 5 estrelas e deixar um comentário
    # Você ganha pontos quando avalia um livro pela primeira vez!
    path('livros/<int:livro_id>/avaliar/', views.adicionar_avaliacao, name='adicionar_avaliacao'),
    
    
    # ==========================================
    # GAMIFICAÇÃO - Pontos e competição
    # ==========================================
    
    # Ver o ranking dos leitores com mais pontos - veja quem lê mais!
    path('ranking/', views.ranking_pontos, name='ranking_pontos'),
    
    # Meu perfil com todas as minhas estatísticas de leitura
    # Quantos livros li, quantos pontos tenho, minha sequência de dias lendo, etc.
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
    
    # Página de celebração quando conclui um livro - CONFETES! 🎉
    path('celebracao/<int:progresso_id>/', views.celebrar_conclusao, name='celebrar_conclusao'),
    
    
    
    #sessao para superusuários
    
    
    # Dashboard de gerenciamento
    path('gerenciar/', views.gerenciar_dashboard, name='gerenciar_dashboard'),
    
    # CRUD Livros
    path('gerenciar/livros/', views.gerenciar_livros, name='gerenciar_livros'),
    path('gerenciar/livros/criar/', views.criar_livro, name='criar_livro'),
    path('gerenciar/livros/<int:livro_id>/editar/', views.editar_livro, name='editar_livro'),
    path('gerenciar/livros/<int:livro_id>/deletar/', views.deletar_livro, name='deletar_livro'),
    
    # CRUD Escritores
    path('gerenciar/escritores/', views.gerenciar_escritores, name='gerenciar_escritores'),
    path('gerenciar/escritores/criar/', views.criar_escritor, name='criar_escritor'),
    path('gerenciar/escritores/<int:escritor_id>/editar/', views.editar_escritor, name='editar_escritor'),
    path('gerenciar/escritores/<int:escritor_id>/deletar/', views.deletar_escritor, name='deletar_escritor'),
    
    # CRUD Editoras
    path('gerenciar/editoras/', views.gerenciar_editoras, name='gerenciar_editoras'),
    path('gerenciar/editoras/criar/', views.criar_editora, name='criar_editora'),
    path('gerenciar/editoras/<int:editora_id>/editar/', views.editar_editora, name='editar_editora'),
    path('gerenciar/editoras/<int:editora_id>/deletar/', views.deletar_editora, name='deletar_editora'),
]
