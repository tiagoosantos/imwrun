import pandas as pd
from functools import wraps
from typing import Callable, Any

from database.transaction import readonly


class RelatorioService:

    @readonly
    def gerar_relatorio_mensal( self, mes: str, *, conn=None) -> str:
        """
        mes no formato: YYYY-MM (ex: 2026-01)
        """

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

        arquivo = f"relatorio_corridas_{mes}.xlsx"
        df.to_excel(arquivo, index=False)

        return arquivo
