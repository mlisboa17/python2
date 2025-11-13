"""
COMANDO PERSONALIZADO DO DJANGO
================================

Este é um comando que você pode executar no terminal para popular o banco de dados
com dados de exemplo (livros, escritores, editoras).

Como usar:
    python manage.py popular_dados

É tipo um "instalador de exemplos" - roda uma vez e pronto!
"""

from django.core.management.base import BaseCommand
from leia_bem.models import Editora, Escritor, Livro


class Command(BaseCommand):
    """
    Comando para popular o banco de dados com dados de exemplo.
    
    Isso é super útil pra testar o sistema sem precisar ficar
    cadastrando tudo manualmente no admin!
    """
    
    # Essa mensagem aparece quando você roda --help
    help = 'Popula o banco de dados com livros, escritores e editoras de exemplo'

    def handle(self, *args, **options):
        """
        Essa é a função principal que roda quando você executa o comando.
        É tipo a "main()" de um programa normal!
        """
        
        # Mostra uma mensagem bonita no terminal
        self.stdout.write(self.style.SUCCESS('🚀 Iniciando população do banco de dados...'))
        
        # ==========================================
        # CRIANDO EDITORAS
        # ==========================================
        self.stdout.write('📚 Criando editoras...')
        
        editoras_data = [
            {'nome': 'Companhia das Letras', 'site': 'https://companhiadasletras.com.br', 'telefone': '(11) 3707-3500'},
            {'nome': 'Record', 'site': 'https://record.com.br', 'telefone': '(21) 2585-2000'},
            {'nome': 'Intrínseca', 'site': 'https://intrinseca.com.br', 'telefone': '(21) 3206-7400'},
            {'nome': 'Rocco', 'site': 'https://rocco.com.br', 'telefone': '(21) 3525-2000'},
            {'nome': 'Globo Livros', 'site': 'https://globolivros.com.br', 'telefone': '(21) 2534-8000'},
        ]
        
        editoras = []
        for data in editoras_data:
            # get_or_create = "pega se existir, senão cria um novo"
            editora, created = Editora.objects.get_or_create(
                nome=data['nome'],
                defaults={'site': data['site'], 'telefone': data['telefone']}
            )
            editoras.append(editora)
            if created:
                self.stdout.write(f'  ✅ Criada: {editora.nome}')
            else:
                self.stdout.write(f'  ⏭️  Já existe: {editora.nome}')
        
        # ==========================================
        # CRIANDO ESCRITORES
        # ==========================================
        self.stdout.write('\n✍️  Criando escritores...')
        
        escritores_data = [
            {
                'nome': 'Machado de Assis',
                'email': 'machado@classicos.br',
                'bibliografia': 'Considerado um dos maiores escritores brasileiros. Autor de Dom Casmurro, Memórias Póstumas de Brás Cubas, entre outros.'
            },
            {
                'nome': 'Clarice Lispector',
                'email': 'clarice@literatura.br',
                'bibliografia': 'Uma das escritoras brasileiras mais importantes. Conhecida por sua prosa introspectiva e inovadora.'
            },
            {
                'nome': 'Jorge Amado',
                'email': 'jorge@bahia.br',
                'bibliografia': 'Escritor baiano conhecido por obras que retratam a cultura e o povo da Bahia.'
            },
            {
                'nome': 'Paulo Coelho',
                'email': 'paulo@alquimista.br',
                'bibliografia': 'Autor brasileiro mais vendido no mundo. Conhecido por O Alquimista e outras obras de ficção.'
            },
            {
                'nome': 'Cecília Meireles',
                'email': 'cecilia@poesia.br',
                'bibliografia': 'Poetisa, pintora, professora e jornalista brasileira. Uma das vozes líricas mais importantes da língua portuguesa.'
            },
        ]
        
        escritores = []
        for data in escritores_data:
            escritor, created = Escritor.objects.get_or_create(
                nome=data['nome'],
                defaults={'email': data['email'], 'bibliografia': data['bibliografia']}
            )
            escritores.append(escritor)
            if created:
                self.stdout.write(f'  ✅ Criado: {escritor.nome}')
            else:
                self.stdout.write(f'  ⏭️  Já existe: {escritor.nome}')
        
        # ==========================================
        # CRIANDO LIVROS
        # ==========================================
        self.stdout.write('\n📖 Criando livros...')
        
        livros_data = [
            {
                'titulo': 'Dom Casmurro',
                'escritor': escritores[0],  # Machado de Assis
                'editora': editoras[0],     # Companhia das Letras
                'ano_publicacao': 1899,
                'numero_paginas': 256,
            },
            {
                'titulo': 'Memórias Póstumas de Brás Cubas',
                'escritor': escritores[0],  # Machado de Assis
                'editora': editoras[0],
                'ano_publicacao': 1881,
                'numero_paginas': 368,
            },
            {
                'titulo': 'A Hora da Estrela',
                'escritor': escritores[1],  # Clarice Lispector
                'editora': editoras[3],     # Rocco
                'ano_publicacao': 1977,
                'numero_paginas': 88,
            },
            {
                'titulo': 'A Paixão Segundo G.H.',
                'escritor': escritores[1],  # Clarice Lispector
                'editora': editoras[3],
                'ano_publicacao': 1964,
                'numero_paginas': 176,
            },
            {
                'titulo': 'Capitães da Areia',
                'escritor': escritores[2],  # Jorge Amado
                'editora': editoras[0],
                'ano_publicacao': 1937,
                'numero_paginas': 280,
            },
            {
                'titulo': 'Gabriela, Cravo e Canela',
                'escritor': escritores[2],  # Jorge Amado
                'editora': editoras[0],
                'ano_publicacao': 1958,
                'numero_paginas': 424,
            },
            {
                'titulo': 'O Alquimista',
                'escritor': escritores[3],  # Paulo Coelho
                'editora': editoras[3],
                'ano_publicacao': 1988,
                'numero_paginas': 208,
            },
            {
                'titulo': 'O Diário de um Mago',
                'escritor': escritores[3],  # Paulo Coelho
                'editora': editoras[3],
                'ano_publicacao': 1987,
                'numero_paginas': 256,
            },
            {
                'titulo': 'Vaga Música',
                'escritor': escritores[4],  # Cecília Meireles
                'editora': editoras[4],     # Globo Livros
                'ano_publicacao': 1942,
                'numero_paginas': 120,
            },
            {
                'titulo': 'Romanceiro da Inconfidência',
                'escritor': escritores[4],  # Cecília Meireles
                'editora': editoras[4],
                'ano_publicacao': 1953,
                'numero_paginas': 312,
            },
        ]
        
        livros_criados = 0
        livros_existentes = 0
        
        for data in livros_data:
            livro, created = Livro.objects.get_or_create(
                titulo=data['titulo'],
                defaults={
                    'escritor': data['escritor'],
                    'editora': data['editora'],
                    'ano_publicacao': data['ano_publicacao'],
                    'numero_paginas': data['numero_paginas'],
                }
            )
            if created:
                livros_criados += 1
                self.stdout.write(f'  ✅ Criado: {livro.titulo} - {livro.escritor.nome}')
            else:
                livros_existentes += 1
                self.stdout.write(f'  ⏭️  Já existe: {livro.titulo}')
        
        # ==========================================
        # RESUMO FINAL
        # ==========================================
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✨ População do banco de dados concluída!'))
        self.stdout.write('='*60)
        self.stdout.write(f'📚 Editoras: {len(editoras)} no total')
        self.stdout.write(f'✍️  Escritores: {len(escritores)} no total')
        self.stdout.write(f'📖 Livros criados: {livros_criados}')
        self.stdout.write(f'📖 Livros já existentes: {livros_existentes}')
        self.stdout.write(f'📖 Total de livros: {livros_criados + livros_existentes}')
        self.stdout.write('\n🎉 Agora você pode testar o sistema com esses dados!')
        self.stdout.write('🌐 Acesse: http://127.0.0.1:8000/\n')
