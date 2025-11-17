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
    
    # Se usuário logado, verificar quais livros já estão na biblioteca
    livros_na_biblioteca = []
    if request.user.is_authenticated:
        livros_na_biblioteca = ProgressoLeitura.objects.filter(
            usuario=request.user
        ).values_list('livro_id', flat=True)
    
    context = {
        'livros_destaque': livros_destaque,
        'livros_na_biblioteca': livros_na_biblioteca,
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
    
    # Se usuário logado, verificar quais livros já estão na biblioteca
    livros_na_biblioteca = []
    if request.user.is_authenticated:
        livros_na_biblioteca = ProgressoLeitura.objects.filter(
            usuario=request.user
        ).values_list('livro_id', flat=True)
    
    context = {
        'livros': livros,
        'query': query,
        'livros_na_biblioteca': livros_na_biblioteca,
    }
    return render(request, 'leia_bem/lista_livros.html', context)


def detalhe_livro(request, livro_id):
    """Detalhes de um livro específico"""
    from random import choice
    from .models import PARODIAS_MOTIVACIONAIS
    
    livro = get_object_or_404(Livro, pk=livro_id)
    avaliacoes = livro.avaliacoes.select_related('usuario').order_by('-criado')
    
    progresso = None
    avaliacao_usuario = None
    pode_avaliar = False
    parodia_motivacional = None
    
    if request.user.is_authenticated:
        progresso = ProgressoLeitura.objects.filter(usuario=request.user, livro=livro).first()
        avaliacao_usuario = Avaliacao.objects.filter(usuario=request.user, livro=livro).first()
        
        if progresso:
            pode_avaliar = progresso.status == 'CONCLUIDO'
            if not pode_avaliar:
                parodia_motivacional = choice(PARODIAS_MOTIVACIONAIS)
    
    return render(request, 'leia_bem/detalhe_livro.html', {
        'livro': livro,
        'avaliacoes': avaliacoes,
        'progresso': progresso,
        'avaliacao_usuario': avaliacao_usuario,
        'pode_avaliar': pode_avaliar,
        'parodia_motivacional': parodia_motivacional,
    })


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
    
    # Verifica de onde veio a requisição e redireciona de volta
    referrer = request.META.get('HTTP_REFERER')
    if referrer and '/livros/' in referrer and str(livro_id) in referrer:
        # Se veio da página de detalhes, volta para detalhes
        return redirect('detalhe_livro', livro_id=livro_id)
    else:
        # Se veio de outra página (lista ou index), volta para lá
        return redirect(referrer if referrer else 'lista_livros')


@login_required
def atualizar_progresso(request, progresso_id):
    """Atualiza o progresso de leitura"""
    progresso = get_object_or_404(ProgressoLeitura, pk=progresso_id, usuario=request.user)
    
    if progresso.status == 'CONCLUIDO':
        messages.warning(request, 'Este livro já foi concluído e não pode ser editado!')
        return redirect('meus_livros')
    
    if request.method == 'POST':
        pagina = request.POST.get('pagina_atual')
        status = request.POST.get('status')
        
        # Se marcou como concluído manualmente
        if status == 'CONCLUIDO':
            progresso.atualizar_por_pagina(progresso.livro.numero_paginas or 0)
            return redirect('celebrar_conclusao', progresso_id=progresso.id)
        
        # Atualiza página atual
        if pagina:
            try:
                acabou_de_concluir = progresso.atualizar_por_pagina(int(pagina))
                if acabou_de_concluir:
                    return redirect('celebrar_conclusao', progresso_id=progresso.id)
            except ValueError:
                messages.error(request, 'Número de página inválido.')
                return redirect('meus_livros')
        
        # Apenas muda status
        if status in dict(ProgressoLeitura.STATUS_CHOICES):
            progresso.status = status
            progresso.save(update_fields=['status'])
        
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
    
    # Verificar se o usuário terminou de ler o livro
    try:
        progresso = ProgressoLeitura.objects.get(usuario=request.user, livro=livro)
        if progresso.status != 'CONCLUIDO':
            messages.error(request, 'Você precisa terminar de ler o livro antes de avaliá-lo!')
            return redirect('detalhe_livro', livro_id=livro_id)
    except ProgressoLeitura.DoesNotExist:
        messages.error(request, 'Você precisa adicionar o livro à sua lista e terminá-lo antes de avaliá-lo!')
        return redirect('detalhe_livro', livro_id=livro_id)
    
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
    """Página de celebração quando usuário conclui um livro"""
    from django.db.models import Sum
    from django.contrib.auth import get_user_model
    from decimal import Decimal
    from .models import JANJETAS_PODIO_PRIMEIRO, JANJETAS_PODIO_SEGUNDO, JANJETAS_PODIO_TERCEIRO
    
    User = get_user_model()
    progresso = get_object_or_404(ProgressoLeitura, pk=progresso_id, usuario=request.user)
    
    # Função auxiliar para calcular ranking
    def obter_ranking():
        usuarios = User.objects.annotate(
            total_pontos=Sum('progressoleitura__pontos')
        ).filter(total_pontos__gt=0).order_by('-total_pontos')
        
        for idx, usuario in enumerate(usuarios, start=1):
            if usuario.id == request.user.id:
                return idx, usuarios.count()
        return None, usuarios.count()
    
    # Ranking antes do bônus
    posicao_antiga, total_usuarios = obter_ranking()
    
    # Aplica bônus de pódio
    bonus_podio = Decimal('0.00')
    bonus_map = {1: JANJETAS_PODIO_PRIMEIRO, 2: JANJETAS_PODIO_SEGUNDO, 3: JANJETAS_PODIO_TERCEIRO}
    
    if posicao_antiga and posicao_antiga in bonus_map:
        bonus_podio = Decimal(str(bonus_map[posicao_antiga]))
        progresso.pontos += bonus_podio
        progresso.save(update_fields=['pontos'])
    
    # Ranking após bônus
    posicao_ranking, _ = obter_ranking()
    
    return render(request, 'leia_bem/celebracao.html', {
        'progresso': progresso,
        'livro': progresso.livro,
        'posicao_ranking': posicao_ranking,
        'total_usuarios': total_usuarios,
        'total_pontos': request.user.progressoleitura_set.aggregate(Sum('pontos'))['pontos__sum'] or Decimal('0.00'),
        'livros_concluidos': request.user.progressoleitura_set.filter(status='CONCLUIDO').count(),
        'entrou_no_podio': bool(bonus_podio),
        'bonus_podio': bonus_podio,
        'posicao_podio': posicao_antiga,
    })


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


# ==========================================
# ÁREA DE GERENCIAMENTO (APENAS SUPERUSUÁRIOS)
# ==========================================

from django.contrib.admin.views.decorators import staff_member_required
from .forms import LivroForm, EscritorForm, EditoraForm

@staff_member_required
def gerenciar_dashboard(request):
    """Dashboard de gerenciamento para superusuários"""
    from django.db.models import Count
    
    estatisticas = {
        'total_livros': Livro.objects.count(),
        'total_escritores': Escritor.objects.count(),
        'total_editoras': Editora.objects.count(),
        'total_usuarios': request.user.__class__.objects.count(),
    }
    
    return render(request, 'leia_bem/gerenciar/dashboard.html', {'estatisticas': estatisticas})


# ========== CRUD LIVROS ==========

@staff_member_required
def gerenciar_livros(request):
    """Lista todos os livros para gerenciamento"""
    livros = Livro.objects.select_related('escritor', 'editora').all()
    return render(request, 'leia_bem/gerenciar/livros_lista.html', {'livros': livros})


@staff_member_required
def criar_livro(request):
    """Cria um novo livro"""
    if request.method == 'POST':
        form = LivroForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Livro criado com sucesso!')
            return redirect('gerenciar_livros')
    else:
        form = LivroForm()
    
    return render(request, 'leia_bem/gerenciar/livro_form.html', {'form': form, 'acao': 'Criar'})


@staff_member_required
def editar_livro(request, livro_id):
    """Edita um livro existente"""
    livro = get_object_or_404(Livro, pk=livro_id)
    
    if request.method == 'POST':
        form = LivroForm(request.POST, request.FILES, instance=livro)
        if form.is_valid():
            form.save()
            messages.success(request, 'Livro atualizado com sucesso!')
            return redirect('gerenciar_livros')
    else:
        form = LivroForm(instance=livro)
    
    return render(request, 'leia_bem/gerenciar/livro_form.html', {'form': form, 'acao': 'Editar', 'livro': livro})


@staff_member_required
def deletar_livro(request, livro_id):
    """Deleta um livro"""
    livro = get_object_or_404(Livro, pk=livro_id)
    
    if request.method == 'POST':
        titulo = livro.titulo
        livro.delete()
        messages.success(request, f'Livro "{titulo}" deletado com sucesso!')
        return redirect('gerenciar_livros')
    
    return render(request, 'leia_bem/gerenciar/livro_confirmar_delete.html', {'livro': livro})


# ========== CRUD ESCRITORES ==========

@staff_member_required
def gerenciar_escritores(request):
    """Lista todos os escritores para gerenciamento"""
    escritores = Escritor.objects.annotate(total_livros=Count('livros')).all()
    return render(request, 'leia_bem/gerenciar/escritores_lista.html', {'escritores': escritores})


@staff_member_required
def criar_escritor(request):
    """Cria um novo escritor"""
    if request.method == 'POST':
        form = EscritorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Escritor(a) criado(a) com sucesso!')
            return redirect('gerenciar_escritores')
    else:
        form = EscritorForm()
    
    return render(request, 'leia_bem/gerenciar/escritor_form.html', {'form': form, 'acao': 'Criar'})


@staff_member_required
def editar_escritor(request, escritor_id):
    """Edita um escritor existente"""
    escritor = get_object_or_404(Escritor, pk=escritor_id)
    
    if request.method == 'POST':
        form = EscritorForm(request.POST, request.FILES, instance=escritor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Escritor(a) atualizado(a) com sucesso!')
            return redirect('gerenciar_escritores')
    else:
        form = EscritorForm(instance=escritor)
    
    return render(request, 'leia_bem/gerenciar/escritor_form.html', {'form': form, 'acao': 'Editar', 'escritor': escritor})


@staff_member_required
def deletar_escritor(request, escritor_id):
    """Deleta um escritor"""
    escritor = get_object_or_404(Escritor, pk=escritor_id)
    
    if request.method == 'POST':
        nome = escritor.nome
        escritor.delete()
        messages.success(request, f'Escritor(a) "{nome}" deletado(a) com sucesso!')
        return redirect('gerenciar_escritores')
    
    return render(request, 'leia_bem/gerenciar/escritor_confirmar_delete.html', {'escritor': escritor})


# ========== CRUD EDITORAS ==========

@staff_member_required
def gerenciar_editoras(request):
    """Lista todas as editoras para gerenciamento"""
    editoras = Editora.objects.all()
    return render(request, 'leia_bem/gerenciar/editoras_lista.html', {'editoras': editoras})


@staff_member_required
def criar_editora(request):
    """Cria uma nova editora"""
    if request.method == 'POST':
        form = EditoraForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Editora criada com sucesso!')
            return redirect('gerenciar_editoras')
    else:
        form = EditoraForm()
    
    return render(request, 'leia_bem/gerenciar/editora_form.html', {'form': form, 'acao': 'Criar'})


@staff_member_required
def editar_editora(request, editora_id):
    """Edita uma editora existente"""
    editora = get_object_or_404(Editora, pk=editora_id)
    
    if request.method == 'POST':
        form = EditoraForm(request.POST, instance=editora)
        if form.is_valid():
            form.save()
            messages.success(request, 'Editora atualizada com sucesso!')
            return redirect('gerenciar_editoras')
    else:
        form = EditoraForm(instance=editora)
    
    return render(request, 'leia_bem/gerenciar/editora_form.html', {'form': form, 'acao': 'Editar', 'editora': editora})


@staff_member_required
def deletar_editora(request, editora_id):
    """Deleta uma editora"""
    editora = get_object_or_404(Editora, pk=editora_id)
    
    if request.method == 'POST':
        nome = editora.nome
        editora.delete()
        messages.success(request, f'Editora "{nome}" deletada com sucesso!')
        return redirect('gerenciar_editoras')
    
    return render(request, 'leia_bem/gerenciar/editora_confirmar_delete.html', {'editora': editora})

