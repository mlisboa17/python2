from django.contrib import admin

from .models import Usuario
from .models import Editora
from .models import Escritor
from django.utils.html import format_html

from .models import Livro, ProgressoLeitura, Avaliacao


@admin.register(Editora)
class EditoraAdmin(admin.ModelAdmin):
    list_display = ("nome", "site", "telefone")
    search_fields = ("nome",)
    ordering = ("nome",)  # Ordenação padrão por nome


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "nome_completo", "is_staff", "is_active")
    search_fields = ("username", "email", "nome_completo")
    list_filter = ("is_staff", "is_active") # Filtros laterais para is_staff e is_active
    ordering = ("username",)  


@admin.register(Escritor)
class EscritorAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "foto_preview")
    search_fields = ("nome", "email")

    def foto_preview(self, obj):
        if obj.foto:
            return format_html('<img src="{}" style="height:50px;border-radius:4px;" />', obj.foto.url)
        return "-"
    foto_preview.short_description = "Foto"    





@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ("titulo", "escritor", "ano_publicacao", "numero_paginas", "nota_media", "total_avaliacoes")
    search_fields = ("titulo", "escritor__nome")  # ajuste conforme campo do Escritor
    list_filter = ("editora",)
    ordering = ("titulo",)

@admin.register(ProgressoLeitura)
class ProgressoLeituraAdmin(admin.ModelAdmin):
    list_display = ("usuario", "livro", "pagina_atual", "porcentagem", "pontos", "ultima_sessao")
    search_fields = ("usuario__username", "livro__titulo")

@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ("usuario", "livro", "nota", "criado")
    search_fields = ("usuario__username", "livro__titulo")


