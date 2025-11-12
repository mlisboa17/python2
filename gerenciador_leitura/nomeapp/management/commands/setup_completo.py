"""
COMANDO MESTRE - FAZ TUDO DE UMA VEZ!
=====================================

Este comando executa tudo que você precisa para começar a usar o sistema:
1. Cria/atualiza o superusuário
2. Popula o banco com livros, escritores e editoras

Como usar:
    python manage.py setup_completo

É tipo um "instalador automático" - roda uma vez e tá pronto! 🚀
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Comando que configura tudo automaticamente:
    - Cria superusuário
    - Popula banco de dados
    """
    
    help = 'Configura o sistema completo: cria superusuário e popula dados'

    def handle(self, *args, **options):
        """
        Executa todos os comandos necessários na ordem certa.
        """
        
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS('🚀 SETUP COMPLETO DO SISTEMA'))
        self.stdout.write(self.style.SUCCESS('='*70))
        
        # Passo 1: Criar superusuário
        self.stdout.write('\n📍 PASSO 1: Criando superusuário...\n')
        call_command('criar_super')
        
        # Passo 2: Popular banco de dados
        self.stdout.write('\n📍 PASSO 2: Populando banco de dados...\n')
        call_command('popular_dados')
        
        # Mensagem final
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('✨ SETUP COMPLETO FINALIZADO!'))
        self.stdout.write('='*70)
        self.stdout.write('\n🎯 O QUE VOCÊ PODE FAZER AGORA:')
        self.stdout.write('   1. Acessar o site: http://127.0.0.1:8000/')
        self.stdout.write('   2. Ver os livros cadastrados')
        self.stdout.write('   3. Criar uma conta de usuário')
        self.stdout.write('   4. Adicionar livros à sua lista')
        self.stdout.write('   5. Acessar o admin: http://127.0.0.1:8000/admin/')
        self.stdout.write('      (Login: admin / Senha: admin123)')
        self.stdout.write('\n🎉 Divirta-se!\n')
