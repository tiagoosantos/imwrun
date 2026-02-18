from datetime import datetime


class UsuarioRepository:

    def __init__(self, connection):
        self.conn = connection

    def buscar_por_telegram_id(self, telegram_id: int):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id,
                       nome,
                       nome_confirmado
                FROM usuarios
                WHERE telegram_id = %s
            """, (telegram_id,))
            return cur.fetchone()

    def inserir_ou_atualizar_usuario(self, user):
        """
        Insere usuário se não existir.
        Atualiza dados dinâmicos e ultimo_acesso.
        """

        # Segurança extra: nunca permitir registrar bot
        # if user.is_bot:
        #     return

        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO usuarios (
                    telegram_id,
                    username,
                    first_name,
                    last_name,
                    language_code,
                    is_premium,
                    is_bot,
                    ultimo_acesso
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (telegram_id)
                DO UPDATE SET
                    username = EXCLUDED.username,
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    language_code = EXCLUDED.language_code,
                    is_premium = EXCLUDED.is_premium,
                    ultimo_acesso = NOW()
            """, (
                user.id,
                user.username,
                user.first_name,
                user.last_name,
                user.language_code,
                getattr(user, "is_premium", False),
                False  # Nunca registrar bot
            ))

            # self.conn.commit()

    def atualizar_nome(self, telegram_id: int, nome: str):
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE usuarios
                SET nome = %s,
                    nome_confirmado = TRUE
                WHERE telegram_id = %s
            """, (nome, telegram_id))

            # self.conn.commit()
