"""
Comando para cadastrar novas editoras
"""
from django.core.management.base import BaseCommand
from leia_bem.models import Editora


class Command(BaseCommand):
    help = 'Cadastra novas editoras brasileiras e internacionais'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Iniciando cadastro de editoras...\n')

        # Lista de editoras
        editoras_nomes = [
            'Galera Record',
            'Arqueiro',
            'Intrínseca',
            'Companhia das Letras',
            'Rocco',
            'Paralela',
            'Seguinte',
            'Bertrand Brasil',
            'Alta Life',
            'Citadel',
            'Principis',
            'Todavia',
            'Vélos',
            'Alt',
            'HarperCollins Brasil',
        ]

        contador_criadas = 0
        contador_existentes = 0

        for nome in editoras_nomes:
            editora, created = Editora.objects.get_or_create(nome=nome)
            
            if created:
                self.stdout.write(f"  ✅ Criada: {nome}")
                contador_criadas += 1
            else:
                self.stdout.write(f"  ℹ️  Já existe: {nome}")
                contador_existentes += 1

        self.stdout.write('\n' + '='*60)
        self.stdout.write('✨ Cadastro de editoras concluído!')
        self.stdout.write('='*60)
        self.stdout.write(f'🏢 Editoras criadas: {contador_criadas}')
        self.stdout.write(f'📚 Editoras já existentes: {contador_existentes}')
        self.stdout.write(f'📊 Total processado: {contador_criadas + contador_existentes}')
        self.stdout.write('\n🎉 Editoras prontas!\n')
