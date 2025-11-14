"""
Comando para cadastrar livros brasileiros com suas capas
"""
from django.core.management.base import BaseCommand
from django.core.files import File
from leia_bem.models import Livro, Escritor, Editora
import os


class Command(BaseCommand):
    help = 'Cadastra livros brasileiros clássicos com suas capas'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Iniciando cadastro de livros...\n')

        # Caminho base das capas
        base_path = 'media/livros/capas/'
        
        # Primeiro, garante que as editoras existem
        editoras_data = {
            'Companhia das Letras': 'Uma das maiores editoras do Brasil, fundada em 1986.',
            'Record': 'Editora brasileira fundada em 1942, uma das maiores do país.',
            'Rocco': 'Editora brasileira fundada em 1975, especializada em literatura.',
            'HarperCollins Brasil': 'Braço brasileiro da editora internacional HarperCollins.',
            'Global Editora': 'Editora brasileira fundada em 1973.',
        }

        self.stdout.write('📚 Criando/verificando editoras...')
        editoras = {}
        for nome, descricao in editoras_data.items():
            editora, created = Editora.objects.get_or_create(
                nome=nome,
                defaults={}
            )
            editoras[nome] = editora
            if created:
                self.stdout.write(f'  ✅ Criada: {nome}')
            else:
                self.stdout.write(f'  ℹ️  Já existe: {nome}')

        # Lista de livros com informações completas
        livros_data = [
            {
                'titulo': 'Dom Casmurro',
                'escritor_nome': 'Machado de Assis',
                'editora': editoras['Companhia das Letras'],
                'ano_publicacao': 1899,
                'total_paginas': 256,
                'sinopse': 'Romance narrado por Bento Santiago (Bentinho), que relata sua vida desde a infância até a velhice, com foco especial em seu relacionamento com Capitu. A obra levanta a questão da traição, deixando ao leitor a interpretação sobre a culpa ou inocência de Capitu.',
                'isbn': '9788535911664',
                'capa': 'domcasmurro.webp'
            },
            {
                'titulo': 'Memórias Póstumas de Brás Cubas',
                'escritor_nome': 'Machado de Assis',
                'editora': editoras['Companhia das Letras'],
                'ano_publicacao': 1881,
                'total_paginas': 288,
                'sinopse': 'Narrado por um defunto autor, Brás Cubas conta sua vida de forma irônica e pessimista. Considerado o marco inicial do Realismo brasileiro, o romance inova na forma e apresenta uma visão crítica da sociedade.',
                'isbn': '9788535911671',
                'capa': 'memoriaspostumas.webp'
            },
            {
                'titulo': 'A Hora da Estrela',
                'escritor_nome': 'Clarice Lispector',
                'editora': editoras['Rocco'],
                'ano_publicacao': 1977,
                'total_paginas': 88,
                'sinopse': 'A história de Macabéa, uma nordestina que vive no Rio de Janeiro. O romance explora temas como a alienação, a pobreza e a busca por identidade, sendo considerado uma das obras-primas de Clarice Lispector.',
                'isbn': '9788532511010',
                'capa': 'ahoradaestrela.jpg'
            },
            {
                'titulo': 'A Paixão Segundo G.H.',
                'escritor_nome': 'Clarice Lispector',
                'editora': editoras['Rocco'],
                'ano_publicacao': 1964,
                'total_paginas': 176,
                'sinopse': 'G.H., uma escultora de classe média alta, passa por uma experiência transcendental ao encontrar uma barata no quarto de sua empregada. O romance é um mergulho existencial profundo na consciência humana.',
                'isbn': '9788532511027',
                'capa': 'apaixasegundogh.webp'
            },
            {
                'titulo': 'Capitães da Areia',
                'escritor_nome': 'Jorge Amado',
                'editora': editoras['Companhia das Letras'],
                'ano_publicacao': 1937,
                'total_paginas': 280,
                'sinopse': 'Retrata a vida de um grupo de meninos de rua em Salvador, liderados por Pedro Bala. O romance denuncia as condições sociais precárias e a marginalização da infância pobre no Brasil.',
                'isbn': '9788535914666',
                'capa': 'capitaesdeareia.jpg'
            },
            {
                'titulo': 'Gabriela, Cravo e Canela',
                'escritor_nome': 'Jorge Amado',
                'editora': editoras['Companhia das Letras'],
                'ano_publicacao': 1958,
                'total_paginas': 424,
                'sinopse': 'Ambientado em Ilhéus nos anos 1920, narra a história de amor entre Nacib, um árabe dono de bar, e Gabriela, uma retirante sertaneja. O romance explora temas como tradição, modernização e sensualidade.',
                'isbn': '9788535914680',
                'capa': 'gabrielacravoecanela.jpg'
            },
            {
                'titulo': 'O Alquimista',
                'escritor_nome': 'Paulo Coelho',
                'editora': editoras['HarperCollins Brasil'],
                'ano_publicacao': 1988,
                'total_paginas': 224,
                'sinopse': 'Santiago, um jovem pastor andaluz, parte em uma jornada pelo deserto em busca de um tesouro. O livro fala sobre seguir seus sonhos, ouvir seu coração e descobrir sua lenda pessoal.',
                'isbn': '9788595084100',
                'capa': 'oalquimista.webp'
            },
            {
                'titulo': 'O Diário de um Mago',
                'escritor_nome': 'Paulo Coelho',
                'editora': editoras['HarperCollins Brasil'],
                'ano_publicacao': 1987,
                'total_paginas': 256,
                'sinopse': 'Paulo Coelho narra sua peregrinação pelo Caminho de Santiago de Compostela, uma jornada espiritual em busca de autoconhecimento e crescimento pessoal através de ensinamentos místicos.',
                'isbn': '9788595084117',
                'capa': 'o-diario-de-um-mago.jpg'
            },
            {
                'titulo': 'Vaga Música',
                'escritor_nome': 'Cecília Meireles',
                'editora': editoras['Global Editora'],
                'ano_publicacao': 1942,
                'total_paginas': 128,
                'sinopse': 'Coletânea de poemas que explora temas como o tempo, a memória, a solidão e a natureza efêmera da vida. Os versos apresentam a musicalidade característica de Cecília Meireles.',
                'isbn': '9788526006447',
                'capa': 'vagamusica.jpg'
            }
        ]

        self.stdout.write('\n📖 Cadastrando livros...')
        contador_criados = 0
        contador_existentes = 0
        contador_erros = 0

        for livro_info in livros_data:
            try:
                # Busca o escritor
                escritor = Escritor.objects.get(nome=livro_info['escritor_nome'])
                
                # Verifica se o livro já existe
                livro, created = Livro.objects.get_or_create(
                    titulo=livro_info['titulo'],
                    defaults={
                        'escritor': escritor,
                        'editora': livro_info['editora'],
                        'ano_publicacao': livro_info['ano_publicacao'],
                        'total_paginas': livro_info['total_paginas'],
                        'sinopse': livro_info['sinopse'],
                        'isbn': livro_info['isbn']
                    }
                )

                if created:
                    # Se foi criado, adiciona a capa
                    capa_path = os.path.join(base_path, livro_info['capa'])
                    if os.path.exists(capa_path):
                        with open(capa_path, 'rb') as f:
                            livro.capa.save(livro_info['capa'], File(f), save=True)
                        self.stdout.write(f"  ✅ Criado: {livro.titulo} - {escritor.nome}")
                    else:
                        self.stdout.write(f"  ⚠️  Criado sem capa: {livro.titulo} (capa não encontrada)")
                    contador_criados += 1
                else:
                    # Se já existia, tenta adicionar capa se não tiver
                    if not livro.capa:
                        capa_path = os.path.join(base_path, livro_info['capa'])
                        if os.path.exists(capa_path):
                            with open(capa_path, 'rb') as f:
                                livro.capa.save(livro_info['capa'], File(f), save=True)
                            self.stdout.write(f"  🔄 Atualizado com capa: {livro.titulo}")
                    else:
                        self.stdout.write(f"  ℹ️  Já existe: {livro.titulo}")
                    contador_existentes += 1

            except Escritor.DoesNotExist:
                self.stdout.write(f"  ❌ Erro: Escritor '{livro_info['escritor_nome']}' não encontrado para '{livro_info['titulo']}'")
                contador_erros += 1
            except Exception as e:
                self.stdout.write(f"  ❌ Erro ao cadastrar '{livro_info['titulo']}': {str(e)}")
                contador_erros += 1

        self.stdout.write('\n' + '='*60)
        self.stdout.write('✨ Cadastro de livros concluído!')
        self.stdout.write('='*60)
        self.stdout.write(f'📚 Livros criados: {contador_criados}')
        self.stdout.write(f'📖 Livros já existentes: {contador_existentes}')
        self.stdout.write(f'❌ Erros: {contador_erros}')
        self.stdout.write(f'📕 Total processado: {contador_criados + contador_existentes}')
        self.stdout.write('\n🎉 Livros prontos para leitura!\n')
