"""
COMANDO PARA CRIAR UM SUPERUSUÁRIO DE FORMA FÁCIL
==================================================

Este comando cria um superusuário automaticamente sem precisar
ficar digitando senha, email, etc no terminal.

Como usar:
    python manage.py criar_super

É tipo um "atalho" pra criar admin rapidinho!
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    """
    Comando para criar um superusuário de forma rápida e fácil.
    Perfeito pra desenvolvimento e testes!
    """
    
    help = 'Cria um superusuário automaticamente para desenvolvimento'

    def handle(self, *args, **options):
        """
        Cria ou atualiza um superusuário com dados pré-definidos.
        """
        
        # Pega o modelo de usuário (nosso Usuario personalizado)
        User = get_user_model()
        
        # Dados do superusuário
        username = 'admin'
        email = 'admin@admin.com'
        password = 'admin123'
        
        self.stdout.write(self.style.SUCCESS('👤 Criando/Atualizando superusuário...'))
        
        # Verifica se já existe um usuário com esse username
        if User.objects.filter(username=username).exists():
            # Se já existe, atualiza a senha
            user = User.objects.get(username=username)
            user.set_password(password)  # set_password faz o hash da senha
            user.is_superuser = True
            user.is_staff = True
            user.email = email
            user.save()
            
            self.stdout.write(self.style.WARNING(f'⚠️  Usuário "{username}" já existia!'))
            self.stdout.write(self.style.SUCCESS('✅ Senha atualizada para "admin123"'))
        else:
            # Se não existe, cria um novo
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            self.stdout.write(self.style.SUCCESS(f'✅ Superusuário "{username}" criado com sucesso!'))
        
        # Mostra as credenciais
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('🎉 Superusuário pronto para usar!'))
        self.stdout.write('='*60)
        self.stdout.write(f'👤 Username: {username}')
        self.stdout.write(f'📧 Email: {email}')
        self.stdout.write(f'🔑 Senha: {password}')
        self.stdout.write('='*60)
        self.stdout.write('\n🌐 Acesse o admin em: http://127.0.0.1:8000/admin/')
        self.stdout.write('💡 Use essas credenciais para fazer login!\n')
