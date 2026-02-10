from database.connection import get_connection


class UsuarioRepository:
    """
    Persistência da entidade usuário.
    """

    def criar_se_nao_existir(self, telegram_id: int, nome: str) -> None:
        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                """
                INSERT INTO usuarios (telegram_id, nome)
                VALUES (%s, %s)
                ON CONFLICT (telegram_id) DO NOTHING
                """,
                (telegram_id, nome),
            )
            conn.commit()

        finally:
            cur.close()
            conn.close()
