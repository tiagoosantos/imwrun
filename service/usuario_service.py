from repository.usuario_repository import UsuarioRepository


class UsuarioService:

    def __init__(self, connection):
        """
        Service responsável por regras de negócio do usuário.
        """
        self.repo = UsuarioRepository(connection)

    def registrar_ou_atualizar(self, telegram_user):
        """
        Sempre que o usuário interage:
        - Insere se não existir
        - Atualiza dados dinâmicos (username, first_name, last_name)
        - Retorna status do cadastro
        """

        # Insere ou atualiza informações básicas
        self.repo.inserir_ou_atualizar_usuario(telegram_user)

        # Busca usuário atualizado
        usuario = self.repo.buscar_por_telegram_id(telegram_user.id)

        if not usuario:
            return "NOVO"

        # Estrutura esperada do retorno:
        # (telegram_id, nome, nome_confirmado)
        _, nome, nome_confirmado = usuario

        if not nome_confirmado:
            return "AGUARDANDO_NOME"

        return "OK"

    def salvar_nome(self, telegram_id: int, nome: str):
        """
        Atualiza o nome confirmado do usuário.
        """
        self.repo.atualizar_nome(telegram_id, nome)
