"""
Comando para cadastrar escritores com suas fotos
"""
from django.core.management.base import BaseCommand
from django.core.files import File
from leia_bem.models import Escritor
import os


class Command(BaseCommand):
    help = 'Cadastra os escritores brasileiros com suas fotos'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Iniciando cadastro de escritores...\n')

        # Caminho base das fotos
        base_path = 'media/escritores/fotos/'
        
        # Lista de escritores com informações
        escritores_data = [
            {
                'nome': 'Machado de Assis',
                'biografia': 'Joaquim Maria Machado de Assis (1839-1908) foi um escritor brasileiro, considerado por muitos críticos o maior nome da literatura brasileira. Autor de romances como Dom Casmurro e Memórias Póstumas de Brás Cubas.',
                'foto': 'Machado_de_Assis_by_Marc_Ferrez.jpg.webp'
            },
            {
                'nome': 'Clarice Lispector',
                'biografia': 'Clarice Lispector (1920-1977) foi uma escritora e jornalista nascida na Ucrânia e naturalizada brasileira. É considerada uma das escritoras brasileiras mais importantes do século XX. Autora de A Hora da Estrela e A Paixão Segundo G.H.',
                'foto': 'Clarice_Lispector_cropped.jpg'
            },
            {
                'nome': 'Jorge Amado',
                'biografia': 'Jorge Leal Amado de Faria (1912-2001) foi um dos mais famosos e traduzidos escritores brasileiros de todos os tempos. Autor de Capitães da Areia, Gabriela Cravo e Canela, entre outros clássicos.',
                'foto': 'Jorge_Amado_gtfy.00010.jpg'
            },
            {
                'nome': 'Paulo Coelho',
                'biografia': 'Paulo Coelho (1947-) é um romancista, dramaturgo e letrista brasileiro. É o escritor de língua portuguesa mais lido do mundo. Autor de O Alquimista, best-seller mundial traduzido para mais de 80 idiomas.',
                'foto': 'Paulo_Coelho_June_2024.jpg'
            },
            {
                'nome': 'Cecília Meireles',
                'biografia': 'Cecília Benevides de Carvalho Meireles (1901-1964) foi uma poetisa, pintora, professora e jornalista brasileira. É considerada uma das vozes líricas mais importantes da literatura brasileira. Autora de Romanceiro da Inconfidência e Viagem.',
                'foto': 'Cecília-Meireles.jpg'
            },
            {
                'nome': 'Ariano Suassuna',
                'biografia': 'Ariano Vilar Suassuna (1927-2014) foi um dramaturgo, romancista e poeta brasileiro. Idealizador do Movimento Armorial e autor de O Auto da Compadecida, uma das obras mais importantes do teatro brasileiro.',
                'foto': 'ArianoSuassuna.jpg'
            }
        ]

        contador_criados = 0
        contador_existentes = 0

        for escritor_info in escritores_data:
            # Verifica se o escritor já existe
            escritor, created = Escritor.objects.get_or_create(
                nome=escritor_info['nome'],
                defaults={
                    'bibliografia': escritor_info['biografia']
                }
            )

            if created:
                # Se foi criado, adiciona a foto
                foto_path = os.path.join(base_path, escritor_info['foto'])
                if os.path.exists(foto_path):
                    with open(foto_path, 'rb') as f:
                        escritor.foto.save(escritor_info['foto'], File(f), save=True)
                    self.stdout.write(f"  ✅ Criado: {escritor.nome}")
                    contador_criados += 1
                else:
                    self.stdout.write(f"  ⚠️  Criado sem foto: {escritor.nome} (foto não encontrada)")
                    contador_criados += 1
            else:
                # Se já existia, atualiza a bibliografia se estiver vazia
                if not escritor.bibliografia:
                    escritor.bibliografia = escritor_info['biografia']
                    escritor.save()
                
                # Se não tem foto, tenta adicionar
                if not escritor.foto:
                    foto_path = os.path.join(base_path, escritor_info['foto'])
                    if os.path.exists(foto_path):
                        with open(foto_path, 'rb') as f:
                            escritor.foto.save(escritor_info['foto'], File(f), save=True)
                        self.stdout.write(f"  🔄 Atualizado com foto: {escritor.nome}")
                    else:
                        self.stdout.write(f"  ⚠️  Já existe: {escritor.nome} (sem foto)")
                else:
                    self.stdout.write(f"  ℹ️  Já existe: {escritor.nome}")
                contador_existentes += 1

        self.stdout.write('\n' + '='*60)
        self.stdout.write('✨ Cadastro de escritores concluído!')
        self.stdout.write('='*60)
        self.stdout.write(f'✍️  Escritores criados: {contador_criados}')
        self.stdout.write(f'📝 Escritores já existentes: {contador_existentes}')
        self.stdout.write(f'📚 Total de escritores: {contador_criados + contador_existentes}')
        self.stdout.write('\n🎉 Escritores prontos para uso!\n')
