from repository.usuario_repository import UsuarioRepository


class UsuarioService:
    def __init__(self):
        self.repo = UsuarioRepository()

    def registrar_usuario(self, telegram_id: int, nome: str) -> None:
        """
        Regra simples hoje, extensível amanhã.
        """
        self.repo.criar_se_nao_existir(
            telegram_id=telegram_id,
            nome=nome,
        )
