from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from .models import Livro, ProgressoLeitura, Avaliacao, Escritor, Editora
from .forms import SignUpForm


def index(request):
    """Página inicial"""
    livros_destaque = Livro.objects.order_by('-nota_media')[:6]
    context = {
        'livros_destaque': livros_destaque,
    }
    return render(request, 'leia_bem/index.html', context)


def lista_livros(request):
    """Lista todos os livros com busca e filtros"""
    livros = Livro.objects.all()
    
    # Busca
    query = request.GET.get('q')
    if query:
        livros = livros.filter(
            Q(titulo__icontains=query) |
            Q(escritor__nome__icontains=query) |
            Q(editora__nome__icontains=query)
        )
    
    # Ordenação
    ordem = request.GET.get('ordem', '-nota_media')
    livros = livros.order_by(ordem)
    
    context = {
        'livros': livros,
        'query': query,
    }
    return render(request, 'leia_bem/lista_livros.html', context)


def detalhe_livro(request, livro_id):
    """Detalhes de um livro específico"""
    livro = get_object_or_404(Livro, pk=livro_id)
    avaliacoes = livro.avaliacoes.all().order_by('-criado')
    
    # Se usuário logado, verificar progresso e avaliação
    progresso = None
    avaliacao_usuario = None
    if request.user.is_authenticated:
        try:
            progresso = ProgressoLeitura.objects.get(usuario=request.user, livro=livro)
        except ProgressoLeitura.DoesNotExist:
            pass
        
        try:
            avaliacao_usuario = Avaliacao.objects.get(usuario=request.user, livro=livro)
        except Avaliacao.DoesNotExist:
            pass
    
    context = {
        'livro': livro,
        'avaliacoes': avaliacoes,
        'progresso': progresso,
        'avaliacao_usuario': avaliacao_usuario,
    }
    return render(request, 'leia_bem/detalhe_livro.html', context)


@login_required
def meus_livros(request):
    """Lista os livros do usuário com progresso"""
    progressos = ProgressoLeitura.objects.filter(usuario=request.user).select_related('livro')
    
    # Filtro por status
    status = request.GET.get('status')
    if status:
        progressos = progressos.filter(status=status)
    
    context = {
        'progressos': progressos,
    }
    return render(request, 'leia_bem/meus_livros.html', context)


@login_required
def adicionar_livro_leitura(request, livro_id):
    """Adiciona um livro à lista de leitura do usuário"""
    livro = get_object_or_404(Livro, pk=livro_id)
    
    progresso, created = ProgressoLeitura.objects.get_or_create(
        usuario=request.user,
        livro=livro,
        defaults={
            'pagina_atual': 0,
            'porcentagem': 0.00,
            'pontos': 0,
            'status': 'LENDO'
        }
    )
    
    if created:
        messages.success(request, f'"{livro.titulo}" adicionado à sua lista de leitura!')
    else:
        messages.info(request, f'"{livro.titulo}" já está na sua lista.')
    
    return redirect('detalhe_livro', livro_id=livro_id)


@login_required
def atualizar_progresso(request, progresso_id):
    """Atualiza o progresso de leitura"""
    progresso = get_object_or_404(ProgressoLeitura, pk=progresso_id, usuario=request.user)
    
    if request.method == 'POST':
        pagina = request.POST.get('pagina_atual')
        status = request.POST.get('status')
        livro_concluido = False
        
        if pagina:
            try:
                pagina = int(pagina)
                pagina_anterior = progresso.pagina_atual
                progresso.atualizar_por_pagina(pagina)
                
                # Se chegou no final do livro e não estava concluído antes
                if progresso.porcentagem >= 100 and progresso.status != 'CONCLUIDO':
                    livro_concluido = True
                    
            except ValueError:
                messages.error(request, 'Número de página inválido.')
        
        if status and status in dict(ProgressoLeitura.STATUS_CHOICES):
            # Se mudou de outro status para CONCLUIDO
            if status == 'CONCLUIDO' and progresso.status != 'CONCLUIDO':
                livro_concluido = True
            progresso.status = status
            progresso.save(update_fields=['status'])
        
        # Se concluiu o livro, redireciona para página de celebração
        if livro_concluido:
            return redirect('celebrar_conclusao', progresso_id=progresso.id)
        
        messages.success(request, 'Progresso atualizado com sucesso!')
    
    return redirect('meus_livros')


@login_required
def registrar_sessao_leitura(request, progresso_id):
    """Registra uma sessão de leitura e ganha pontos"""
    progresso = get_object_or_404(ProgressoLeitura, pk=progresso_id, usuario=request.user)
    
    if request.method == 'POST':
        # Pega quantas páginas foram lidas nesta sessão
        paginas_lidas = request.POST.get('paginas_lidas', 0)
        
        try:
            paginas_lidas = int(paginas_lidas)
            if paginas_lidas > 0:
                # Atualiza a página atual somando as páginas lidas
                nova_pagina = progresso.pagina_atual + paginas_lidas
                progresso.atualizar_por_pagina(nova_pagina)
        except (ValueError, TypeError):
            paginas_lidas = 0
        
        # Registra a sessão (ganha pontos por ler)
        pontos_ganhos = progresso.registrar_sessao()
        
        # Verifica se concluiu o livro
        livro_concluido = progresso.porcentagem >= 100 and progresso.status != 'CONCLUIDO'
        if livro_concluido:
            progresso.status = 'CONCLUIDO'
            progresso.save(update_fields=['status'])
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'pontos_ganhos': pontos_ganhos,
                'total_pontos': progresso.pontos,
                'total_sessoes': progresso.total_sessoes,
                'sequencia_atual': progresso.sequencia_atual,
                'pagina_atual': progresso.pagina_atual,
                'porcentagem': float(progresso.porcentagem),
                'livro_concluido': livro_concluido,
                'progresso_id': progresso.id,
            })
        
        # Se concluiu o livro, redireciona para celebração
        if livro_concluido:
            return redirect('celebrar_conclusao', progresso_id=progresso.id)
        
        messages.success(request, f'Sessão registrada! Você ganhou {pontos_ganhos} pontos! (+{paginas_lidas} páginas)')
        return redirect('meus_livros')
    
    # Se não for POST, só redireciona
    return redirect('meus_livros')


@login_required
def adicionar_avaliacao(request, livro_id):
    """Adiciona ou atualiza avaliação de um livro"""
    livro = get_object_or_404(Livro, pk=livro_id)
    
    if request.method == 'POST':
        nota = request.POST.get('nota')
        comentario = request.POST.get('comentario', '')
        
        try:
            nota = int(nota)
            if 1 <= nota <= 5:
                avaliacao, created = Avaliacao.objects.update_or_create(
                    usuario=request.user,
                    livro=livro,
                    defaults={
                        'nota': nota,
                        'comentario': comentario,
                    }
                )
                
                if created:
                    messages.success(request, 'Avaliação adicionada com sucesso!')
                else:
                    messages.success(request, 'Avaliação atualizada com sucesso!')
            else:
                messages.error(request, 'A nota deve estar entre 1 e 5.')
        except (ValueError, TypeError):
            messages.error(request, 'Nota inválida.')
    
    return redirect('detalhe_livro', livro_id=livro_id)


@login_required
def ranking_pontos(request):
    """Exibe o ranking de usuários por pontos"""
    from django.db.models import Sum
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    # Calcula total de pontos por usuário
    usuarios_com_pontos = User.objects.annotate(
        total_pontos=Sum('progressoleitura__pontos')
    ).filter(total_pontos__gt=0).order_by('-total_pontos')[:50]
    
    context = {
        'ranking': usuarios_com_pontos,
    }
    return render(request, 'leia_bem/ranking.html', context)


@login_required
def perfil_usuario(request):
    """Perfil do usuário com estatísticas"""
    from django.db.models import Sum, Avg
    
    progressos = ProgressoLeitura.objects.filter(usuario=request.user)
    
    estatisticas = {
        'total_livros': progressos.count(),
        'livros_concluidos': progressos.filter(status='CONCLUIDO').count(),
        'livros_lendo': progressos.filter(status='LENDO').count(),
        'total_pontos': progressos.aggregate(Sum('pontos'))['pontos__sum'] or 0,
        'total_sessoes': progressos.aggregate(Sum('total_sessoes'))['total_sessoes__sum'] or 0,
        'maior_sequencia': progressos.aggregate(Sum('maior_sequencia_diaria'))['maior_sequencia_diaria__sum'] or 0,
    }
    
    avaliacoes = Avaliacao.objects.filter(usuario=request.user)
    estatisticas['total_avaliacoes'] = avaliacoes.count()
    estatisticas['media_notas'] = avaliacoes.aggregate(Avg('nota'))['nota__avg'] or 0
    
    context = {
        'estatisticas': estatisticas,
        'progressos_recentes': progressos.order_by('-atualizado')[:5],
        'avaliacoes_recentes': avaliacoes.order_by('-criado')[:5],
    }
    return render(request, 'leia_bem/perfil.html', context)


@login_required
def celebrar_conclusao(request, progresso_id):
    """
    Página de celebração quando o usuário conclui um livro!
    Mostra confetes, parabeniza e exibe a posição no ranking.
    """
    from django.db.models import Sum
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    progresso = get_object_or_404(ProgressoLeitura, pk=progresso_id, usuario=request.user)
    
    # Calcula a posição no ranking
    usuarios_com_pontos = User.objects.annotate(
        total_pontos=Sum('progressoleitura__pontos')
    ).filter(total_pontos__gt=0).order_by('-total_pontos')
    
    # Encontra a posição do usuário atual
    posicao_ranking = None
    total_usuarios = usuarios_com_pontos.count()
    
    for idx, usuario in enumerate(usuarios_com_pontos, start=1):
        if usuario.id == request.user.id:
            posicao_ranking = idx
            break
    
    # Calcula total de pontos do usuário
    total_pontos = request.user.progressoleitura_set.aggregate(
        Sum('pontos')
    )['pontos__sum'] or 0
    
    # Total de livros concluídos
    livros_concluidos = request.user.progressoleitura_set.filter(
        status='CONCLUIDO'
    ).count()
    
    context = {
        'progresso': progresso,
        'livro': progresso.livro,
        'posicao_ranking': posicao_ranking,
        'total_usuarios': total_usuarios,
        'total_pontos': total_pontos,
        'livros_concluidos': livros_concluidos,
    }
    
    return render(request, 'leia_bem/celebracao.html', context)


def signup(request):
    """
    Página de Cadastro (Sign Up)
    
    Aqui o novo usuário cria sua conta no sistema.
    Funciona assim:
    1. Se ele chegou aqui clicando no link (GET), mostra o formulário vazio
    2. Se ele preencheu e enviou (POST), valida os dados e cria a conta
    """
    
    # Se o usuário já está logado, não precisa criar conta! Vai pra home.
    if request.user.is_authenticated:
        messages.info(request, 'Você já está logado!')
        return redirect('index')
    
    if request.method == 'POST':
        # O usuário preencheu e enviou o formulário
        form = SignUpForm(request.POST)
        
        # Verifica se tá tudo certo (senhas iguais, email válido, etc)
        if form.is_valid():
            # Salva o novo usuário no banco de dados
            user = form.save()
            
            # Loga o usuário automaticamente (assim ele não precisa fazer login depois)
            login(request, user)
            
            # Mostra mensagem de sucesso
            messages.success(
                request, 
                f'Bem-vindo, {user.username}! Sua conta foi criada com sucesso! 🎉'
            )
            
            # Redireciona pra página inicial
            return redirect('index')
    else:
        # Primeira vez que acessa a página, mostra formulário vazio
        form = SignUpForm()
    
    # Envia o formulário pro template
    return render(request, 'leia_bem/signup.html', {'form': form})
    return render(request, 'leia_bem/perfil.html', context)
