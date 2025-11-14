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
    import random
    
    livro = get_object_or_404(Livro, pk=livro_id)
    avaliacoes = livro.avaliacoes.all().order_by('-criado')
    
    # Se usuário logado, verificar progresso e avaliação
    progresso = None
    avaliacao_usuario = None
    pode_avaliar = False
    parodia_motivacional = None
    
    if request.user.is_authenticated:
        try:
            progresso = ProgressoLeitura.objects.get(usuario=request.user, livro=livro)
            # Só pode avaliar se terminou de ler (status CONCLUIDO)
            pode_avaliar = progresso.status == 'CONCLUIDO'
            
            # Se não pode avaliar, escolhe uma paródia aleatória
            if not pode_avaliar:
                parodias = [
                    "🚫 Tipo a Janja bloqueando conta no X: Sua avaliação tá BLOQUEADA até terminar o livro!",
                    "⚖️ Alexandre de Moraes determinou: LEIA TUDO antes de avaliar! Decisão monocrática, sem recurso!",
                    "🔒 O careca do INSS aprovou: Seu benefício de avaliar só sai quando terminar de ler!",
                    "📱 Janja fez um tweet: Quem não lê até o fim não tem moral pra avaliar! #LeiaTudo",
                    "👨‍⚖️ DECISÃO JUDICIAL: Livro incompleto = Avaliação negada! Cumpra a sentença de leitura!",
                    "💼 INSS das avaliações: Documentação incompleta! Faltam as páginas finais do livro!",
                    "🔨 Moraes bateu o martelo: Sem finale, sem estrelinhas! Tá na Constituição... do site!",
                    "🗣️ A Janja falou no Twitter: Vocês têm que ler tudo primeiro pra depois avaliar, viu gente!",
                    "📋 Careca do INSS: Seu processo de avaliação foi INDEFERIDO por falta de leitura completa!",
                    "⚡ Janja mandou bloquear: Avaliação censurada por falta de leitura completa do livro!",
                    "⚖️ STF votou 11x0: Sem Lei da Anistia pra quem não termina de ler! Todos os ministros concordam!",
                    "🏛️ Barroso decretou: Diferente da Anistia, aqui NÃO tem perdão pra leitura incompleta!",
                    "👔 Gilmar Mendes liberou todo mundo... menos você que não terminou o livro! Sem anistia aqui!",
                    "📜 Lei da Anistia existe pra crimes políticos, mas pra avaliação sem leitura NÃO TEM PERDÃO!",
                    "⚖️ Pleno do STF decidiu: Leitura incompleta é IMPERDOÁVEL! Nem anistia, nem habeas corpus!",
                    "🚀 Elon Musk twittou: Even I can't help you unlock this review! Read the book first!",
                    "⚡ Alexandre de Moraes bloqueou o X E sua avaliação! Termine o livro pra liberar!",
                    "🌐 A briga acabou: Elon e Moraes concordam que você precisa LER TUDO antes de avaliar!",
                    "🔐 Moraes mandou derrubar o X... e sua avaliação também caiu! Leia até o fim!",
                    "💰 Elon pagou a multa pro X voltar, mas sua avaliação SÓ volta quando terminar o livro!",
                    "⚖️ Moraes vs Musk: Único acordo que fizeram foi BLOQUEAR sua avaliação até ler tudo!"
                ]
                parodia_motivacional = random.choice(parodias)
                
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
        'pode_avaliar': pode_avaliar,
        'parodia_motivacional': parodia_motivacional,
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
    
    # Não permite editar se já está concluído
    if progresso.status == 'CONCLUIDO':
        messages.warning(request, 'Este livro já foi concluído e não pode ser editado!')
        return redirect('meus_livros')
    
    if request.method == 'POST':
        pagina = request.POST.get('pagina_atual')
        status = request.POST.get('status')
        livro_concluido = False
        
        # Se mudou para CONCLUIDO
        if status == 'CONCLUIDO' and progresso.status != 'CONCLUIDO':
            # Define todas as páginas como lidas
            if progresso.livro.numero_paginas:
                from decimal import Decimal
                from .models import JANJETAS_POR_PAGINA, JANJETAS_BONUS_CONCLUSAO
                
                progresso.pagina_atual = progresso.livro.numero_paginas
                progresso.porcentagem = Decimal('100.00')
                # Calcula Janjetas: todas as páginas * 0.01 + bônus de conclusão
                progresso.pontos = (Decimal(str(progresso.livro.numero_paginas)) * Decimal(str(JANJETAS_POR_PAGINA)) + 
                                   Decimal(str(progresso.livro.numero_paginas)) * Decimal(str(JANJETAS_BONUS_CONCLUSAO)))
            progresso.status = 'CONCLUIDO'
            progresso.save()
            livro_concluido = True
        elif pagina:
            # Atualiza normalmente se não está marcando como concluído
            try:
                pagina = int(pagina)
                # atualizar_por_pagina agora retorna True se acabou de concluir
                acabou_de_concluir = progresso.atualizar_por_pagina(pagina)
                if acabou_de_concluir:
                    livro_concluido = True
                elif status and status in dict(ProgressoLeitura.STATUS_CHOICES):
                    progresso.status = status
                    progresso.save(update_fields=['status'])
                    
            except ValueError:
                messages.error(request, 'Número de página inválido.')
        elif status and status in dict(ProgressoLeitura.STATUS_CHOICES):
            # Apenas mudou o status (sem alterar página)
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
    """
    Página de celebração quando o usuário conclui um livro!
    Mostra confetes, parabeniza e exibe a posição no ranking.
    Se entrou no pódio, dá bônus de Janjetas!
    """
    from django.db.models import Sum
    from django.contrib.auth import get_user_model
    from decimal import Decimal
    from .models import JANJETAS_PODIO_PRIMEIRO, JANJETAS_PODIO_SEGUNDO, JANJETAS_PODIO_TERCEIRO
    
    User = get_user_model()
    progresso = get_object_or_404(ProgressoLeitura, pk=progresso_id, usuario=request.user)
    
    # Calcula total de pontos do usuário ANTES de verificar pódio
    total_pontos_antes = request.user.progressoleitura_set.aggregate(
        Sum('pontos')
    )['pontos__sum'] or Decimal('0.00')
    
    # Calcula a posição no ranking ANTES do bônus de pódio
    usuarios_com_pontos = User.objects.annotate(
        total_pontos=Sum('progressoleitura__pontos')
    ).filter(total_pontos__gt=0).order_by('-total_pontos')
    
    # Encontra a posição ANTIGA do usuário
    posicao_antiga = None
    for idx, usuario in enumerate(usuarios_com_pontos, start=1):
        if usuario.id == request.user.id:
            posicao_antiga = idx
            break
    
    # Verifica se entrou no pódio e aplica bônus
    entrou_no_podio = False
    bonus_podio = Decimal('0.00')
    posicao_podio = None
    
    if posicao_antiga and posicao_antiga <= 3:
        entrou_no_podio = True
        posicao_podio = posicao_antiga
        
        # Aplica bônus baseado na posição
        if posicao_antiga == 1:
            bonus_podio = Decimal(str(JANJETAS_PODIO_PRIMEIRO))
        elif posicao_antiga == 2:
            bonus_podio = Decimal(str(JANJETAS_PODIO_SEGUNDO))
        elif posicao_antiga == 3:
            bonus_podio = Decimal(str(JANJETAS_PODIO_TERCEIRO))
        
        # Adiciona o bônus aos pontos do progresso
        progresso.pontos += bonus_podio
        progresso.save(update_fields=['pontos'])
    
    # Recalcula a posição APÓS o bônus
    usuarios_com_pontos = User.objects.annotate(
        total_pontos=Sum('progressoleitura__pontos')
    ).filter(total_pontos__gt=0).order_by('-total_pontos')
    
    posicao_ranking = None
    total_usuarios = usuarios_com_pontos.count()
    
    for idx, usuario in enumerate(usuarios_com_pontos, start=1):
        if usuario.id == request.user.id:
            posicao_ranking = idx
            break
    
    # Calcula total de pontos APÓS o bônus
    total_pontos = request.user.progressoleitura_set.aggregate(
        Sum('pontos')
    )['pontos__sum'] or Decimal('0.00')
    
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
        'entrou_no_podio': entrou_no_podio,
        'bonus_podio': bonus_podio,
        'posicao_podio': posicao_podio,
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
