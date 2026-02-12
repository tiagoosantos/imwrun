from database.connection import get_connection


class UsuarioRepository:

    def __init__(self, connection):
        self.conn = connection

    def buscar_por_telegram_id(self, telegram_id: int):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, nome, nome_confirmado
                FROM usuarios
                WHERE telegram_id = %s
            """, (telegram_id,))
            return cur.fetchone()

    def inserir_usuario_inicial(self, telegram_id, username, first_name):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO usuarios (
                    telegram_id,
                    username,
                    telegram_first_name
                )
                VALUES (%s, %s, %s)
                ON CONFLICT (telegram_id) DO NOTHING
            """, (
                telegram_id,
                username,
                first_name
            ))
            self.conn.commit()

    def atualizar_nome(self, telegram_id: int, nome: str):
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE usuarios
                SET nome = %s,
                    nome_confirmado = TRUE
                WHERE telegram_id = %s
            """, (nome, telegram_id))
            self.conn.commit()

