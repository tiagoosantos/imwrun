from repository.usuario_repository import UsuarioRepository


class UsuarioService:

    def __init__(self, connection):
        from repository.usuario_repository import UsuarioRepository
        self.repo = UsuarioRepository(connection)

    def registrar_ou_atualizar(self, telegram_user):
        """
        Sempre que usuário interage:
        - insere se não existir
        - atualiza dados dinâmicos
        """

        self.repo.inserir_ou_atualizar_usuario(telegram_user)

        usuario = self.repo.buscar_por_telegram_id(telegram_user.id)

        if not usuario:
            return "NOVO"

        _, nome, nome_confirmado = usuario

        if not nome_confirmado:
            return "AGUARDANDO_NOME"

        return "OK"

    def salvar_nome(self, telegram_id: int, nome: str):
        self.repo.atualizar_nome(telegram_id, nome)
