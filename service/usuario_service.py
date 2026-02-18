from functools import wraps
from typing import Callable, Any

from repository.usuario_repository import UsuarioRepository
from database.transaction import transactional


class UsuarioService:

    """
    Service responsável por regras de negócio do usuário.
    """

    # ------------------------------------------------------
    # REGISTRAR OU ATUALIZAR
    # ------------------------------------------------------

    @transactional
    def registrar_ou_atualizar(
        self,
        telegram_user,
        *,
        conn=None
    ):
        """
        Sempre que o usuário interage:
        - Insere se não existir
        - Atualiza dados dinâmicos (username, first_name, last_name)
        - Retorna status do cadastro
        """

        if telegram_user.is_bot:
            return "BOT_IGNORADO"

        repo = UsuarioRepository(conn)

        # Insere ou atualiza informações básicas
        repo.inserir_ou_atualizar_usuario(telegram_user)

        # Busca usuário atualizado
        usuario = repo.buscar_por_telegram_id(telegram_user.id)

        if not usuario:
            return "NOVO"

        # Estrutura esperada:
        # (telegram_id, nome, nome_confirmado)
        _, nome, nome_confirmado = usuario

        if not nome_confirmado:
            return "AGUARDANDO_NOME"

        return "OK"

    # ------------------------------------------------------
    # SALVAR NOME CONFIRMADO
    # ------------------------------------------------------

    @transactional
    def salvar_nome(self, telegram_id: int, nome: str, *, conn=None):
        """
        Atualiza o nome confirmado do usuário.
        """

        if not nome or not nome.strip():
            raise ValueError("Nome inválido")

        repo = UsuarioRepository(conn)
        repo.atualizar_nome(telegram_id, nome.strip())
