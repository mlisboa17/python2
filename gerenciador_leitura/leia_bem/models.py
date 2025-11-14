
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db.models import Avg, Count
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Usuario(AbstractUser):
    """
    Modelo de usuário personalizado.
    Usa os campos padrão de AbstractUser (username, password, first_name, last_name, email, is_staff, etc.)
    Adiciona email como único e um campo opcional nome_completo.
    """
    email = models.EmailField("E-mail", unique=True)
    nome_completo = models.CharField("Nome completo", max_length=200, blank=True)

    class Meta:
        db_table = "usuario"
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        # Mostra e-mail se existir, caso contrário username
        return self.email if self.email else self.username
    

class Editora(models.Model):
    nome = models.CharField(max_length=200)
    site = models.URLField(blank=True)
    telefone = models.CharField(max_length=30, blank=True)

    class Meta:
        db_table = "editora"
        indexes = [models.Index(fields=["nome"])]

    def __str__(self):
        return self.nome


class Escritor(models.Model):
    nome = models.CharField(max_length=200)
    email = models.EmailField(unique=True, blank=True, null=True)
    bibliografia = models.TextField(blank=True)
    foto = models.ImageField(upload_to="escritores/fotos/", blank=True)

    class Meta:
        db_table = "escritor"
        indexes = [models.Index(fields=["nome"])]

    def __str__(self):
        return self.nome
    


# Regras de Pontuação
PONTOS_POR_AVALIACAO = 3
PONTOS_BASE_POR_SESSAO = 5
BONUS_DIARIO_CONSECUTIVO = 3
MAX_BONUS_CONSECUTIVO = 15

# Novo Sistema de Janjetas
JANJETAS_POR_PAGINA = 0.01  # Cada página lida = 0.01 Janjetas
JANJETAS_BONUS_CONCLUSAO = 0.10  # Ao terminar: páginas * 0.10 Janjetas
JANJETAS_PODIO_TERCEIRO = 50.00  # Bônus 3º lugar
JANJETAS_PODIO_SEGUNDO = 100.00  # Bônus 2º lugar
JANJETAS_PODIO_PRIMEIRO = 300.00  # Bônus 1º lugar

class Livro(models.Model):
    titulo = models.CharField(max_length=300)
    editora = models.ForeignKey("Editora", on_delete=models.SET_NULL, null=True, blank=True)
    escritor = models.ForeignKey("Escritor", on_delete=models.SET_NULL, null=True, blank=True, related_name="livros")
    ano_publicacao = models.PositiveSmallIntegerField(null=True, blank=True)
    numero_paginas = models.PositiveIntegerField(null=True, blank=True)
    sinopse = models.TextField(blank=True)
    isbn = models.CharField(max_length=20, blank=True)
    capa = models.ImageField(upload_to="livros/capas/", blank=True)

    nota_media = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_avaliacoes = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "livro"
        indexes = [models.Index(fields=["titulo"])]

    def __str__(self):
        return self.titulo

    def atualizar_estatisticas_avaliacao(self):
        agg = self.avaliacoes.aggregate(media=Avg("nota"), total=Count("id"))
        media = agg["media"] or 0
        total = agg["total"] or 0
        changed = False
        if round(float(self.nota_media or 0), 2) != round(float(media or 0), 2):
            self.nota_media = round(media or 0, 2)
            changed = True
        if int(self.total_avaliacoes or 0) != int(total):
            self.total_avaliacoes = int(total)
            changed = True
        if changed:
            self.save(update_fields=["nota_media", "total_avaliacoes"])


class ProgressoLeitura(models.Model):
    STATUS_CHOICES = [
        ("LENDO", "Lendo"),
        ("CONCLUIDO", "Concluído"),
        ("PAUSADO", "Pausado"),
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE)
    pagina_atual = models.PositiveIntegerField(default=0)
    porcentagem = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    pontos = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Mudado para decimal
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="LENDO")
    atualizado = models.DateTimeField(auto_now=True)

    inicio_progresso = models.DateTimeField(null=True, blank=True)
    ultima_sessao = models.DateTimeField(null=True, blank=True)
    total_sessoes = models.PositiveIntegerField(default=0)
    maior_sequencia_diaria = models.PositiveIntegerField(default=0)
    sequencia_atual = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "progresso_leitura"
        unique_together = ("usuario", "livro")
        indexes = [models.Index(fields=["usuario", "livro"])]

    def __str__(self):
        return f"{self.usuario} - {self.livro} ({self.porcentagem}%)"

    def atualizar_por_pagina(self, pagina, pontos_por_pagina=JANJETAS_POR_PAGINA):
        """Atualiza progresso por página. Retorna True se acabou de concluir o livro."""
        from decimal import Decimal
        
        estava_incompleto = self.status != "CONCLUIDO"
        self.pagina_atual = max(0, int(pagina))
        
        if self.livro.numero_paginas:
            porcent = (self.pagina_atual / self.livro.numero_paginas) * 100
            self.porcentagem = round(porcent, 2)
        else:
            self.porcentagem = 0.00
        
        # Calcula Janjetas: páginas lidas * 0.01
        self.pontos = Decimal(str(self.pagina_atual)) * Decimal(str(pontos_por_pagina))
        
        # Se completou agora, adiciona bônus de conclusão
        acabou_de_concluir = False
        if self.porcentagem >= 100 and estava_incompleto:
            self.status = "CONCLUIDO"
            # Bônus: número de páginas * 0.10
            bonus_conclusao = Decimal(str(self.livro.numero_paginas)) * Decimal(str(JANJETAS_BONUS_CONCLUSAO))
            self.pontos += bonus_conclusao
            acabou_de_concluir = True
        elif self.porcentagem >= 100:
            self.status = "CONCLUIDO"
            
        self.atualizado = timezone.now()
        self.save(update_fields=["pagina_atual", "porcentagem", "pontos", "status", "atualizado"])
        
        return acabou_de_concluir

    def registrar_sessao(self, timestamp=None, duracao_minutos=None):
        now = timestamp or timezone.now()
        if not self.inicio_progresso:
            self.inicio_progresso = now

        pontos_ganhos = PONTOS_BASE_POR_SESSAO

        if self.ultima_sessao:
            delta_days = (now.date() - self.ultima_sessao.date()).days
            if delta_days == 0:
                pass
            elif delta_days == 1:
                self.sequencia_atual += 1
            else:
                self.sequencia_atual = 1
        else:
            self.sequencia_atual = 1

        bonus = min(self.sequencia_atual * BONUS_DIARIO_CONSECUTIVO, MAX_BONUS_CONSECUTIVO)
        pontos_ganhos += bonus

        self.total_sessoes = (self.total_sessoes or 0) + 1
        if self.sequencia_atual > (self.maior_sequencia_diaria or 0):
            self.maior_sequencia_diaria = self.sequencia_atual

        self.pontos = (self.pontos or 0) + int(pontos_ganhos)
        self.ultima_sessao = now
        self.atualizado_em = now
        self.save(update_fields=[
            "inicio_progresso", "ultima_sessao", "total_sessoes",
            "sequencia_atual", "maior_sequencia_diaria", "pontos", "atualizado"
        ])

        return int(pontos_ganhos)


class Avaliacao(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE, related_name="avaliacoes")
    nota = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario = models.TextField(blank=True)
    criado = models.DateTimeField(auto_now_add=True)
    atualizado = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "avaliacao"
        unique_together = ("usuario", "livro")
        indexes = [models.Index(fields=["usuario", "livro"])]

    def __str__(self):
        return f"{self.usuario} - {self.livro} ({self.nota}★)"


@receiver(post_save, sender=Avaliacao)
def on_avaliacao_saved(sender, instance, created, **kwargs):
    try:
        instance.livro.atualizar_estatisticas_avaliacao()
    except Livro.DoesNotExist:
        pass

    if created:
        progresso, _ = ProgressoLeitura.objects.get_or_create(
            usuario=instance.usuario,
            livro=instance.livro,
            defaults={"pagina_atual": 0, "porcentagem": 0.00, "pontos": 0, "status": "LENDO"},
        )
        progresso.pontos = progresso.pontos + PONTOS_POR_AVALIACAO
        progresso.atualizado = timezone.now()
        progresso.save(update_fields=["pontos", "atualizado"])


@receiver(post_delete, sender=Avaliacao)
def on_avaliacao_deleted(sender, instance, **kwargs):
    try:
        instance.livro.atualizar_estatisticas_avaliacao()
    except Livro.DoesNotExist:
        pass