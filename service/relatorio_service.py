import pandas as pd
from database.connection import get_connection


class RelatorioService:
    def gerar_relatorio_mensal(self, mes: str):
        """
        mes no formato: YYYY-MM (ex: 2026-01)
        """
        conn = get_connection()

        query = """
        SELECT
            nome,
            km_total,
            tempo_total,
            pace_medio
        FROM corridas_mensais
        WHERE TO_CHAR(mes, 'YYYY-MM') = %s
        """

        df = pd.read_sql(query, conn, params=(mes,))
        conn.close()

        arquivo = f"relatorio_corridas_{mes}.xlsx"
        df.to_excel(arquivo, index=False)

        return arquivo
