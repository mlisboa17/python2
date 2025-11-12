from django.urls import path
from . import views

urlpatterns = [
    # ==========================================
    # PÁGINAS PÚBLICAS - Qualquer pessoa pode acessar
    # ==========================================
    
    # Página inicial do site - mostra os livros em destaque
    path('', views.index, name='index'),
    
    # Página de cadastro - cria uma nova conta
    path('cadastro/', views.signup, name='signup'),
    
    # Lista completa de livros disponíveis - permite buscar e filtrar
    path('livros/', views.lista_livros, name='lista_livros'),
    
    # Página de detalhes de um livro específico - mostra informações completas e avaliações
    # Exemplo: livros/5/ mostra os detalhes do livro com ID 5
    path('livros/<int:livro_id>/', views.detalhe_livro, name='detalhe_livro'),
    
    
    # ==========================================
    # ÁREA DO USUÁRIO - Apenas usuários logados podem acessar
    # ==========================================
    
    # Minha biblioteca pessoal - mostra todos os livros que estou lendo
    path('meus-livros/', views.meus_livros, name='meus_livros'),
    
    # Adicionar um livro à minha lista de leitura
    # Exemplo: livros/3/adicionar/ adiciona o livro com ID 3 na minha lista
    path('livros/<int:livro_id>/adicionar/', views.adicionar_livro_leitura, name='adicionar_livro_leitura'),

    
    # ==========================================
    # PROGRESSO DE LEITURA - Acompanhar o quanto já li
    # ==========================================
    
    # Atualizar quantas páginas já li e o status do livro (lendo, pausado, concluído)
    # Exemplo: progresso/7/atualizar/ atualiza meu progresso no livro 7
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
]

