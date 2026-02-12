from repository.usuario_repository import UsuarioRepository


class UsuarioService:

    def __init__(self, connection):
        self.repo = UsuarioRepository(connection)

    def verificar_ou_criar_usuario(self, telegram_user):
        usuario = self.repo.buscar_por_telegram_id(telegram_user.id)

        if not usuario:
            self.repo.inserir_usuario_inicial(
                telegram_user.id,
                telegram_user.username,
                telegram_user.first_name
            )
            return "NOVO"

        if not usuario[2]:  # nome_confirmado
            return "AGUARDANDO_NOME"

        return "OK"

    def salvar_nome(self, telegram_id: int, nome: str):
        self.repo.atualizar_nome(telegram_id, nome)
