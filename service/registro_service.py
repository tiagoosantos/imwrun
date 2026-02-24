from bot.state.registro_state import registro_temp, limpar_sessao
from bot.utils.bot_utils import formatar_tempo, formatar_distancia
from bot.keyboards.registro_keyboard import teclado_confirmacao


def mostrar_resumo_final(bot, services, chat_id):

    dados = registro_temp.get(chat_id)
    corrida_service = services["corrida"]

    tempo_formatado = formatar_tempo(dados["tempo_segundos"])
    distancia_formatada = formatar_distancia(dados["distancia_metros"])

    pace_segundos = dados.get("pace_segundos")

    if pace_segundos is None:
        pace_segundos = corrida_service.calcular_pace(
            dados["tempo_segundos"],
            dados["distancia_metros"]
        )

    pace_min = pace_segundos // 60
    pace_sec = pace_segundos % 60
    pace_formatado = f"{pace_min:02d}:{pace_sec:02d}"

    data_info = (
        dados["data_corrida"].strftime("%d/%m/%Y %H:%M")
        if dados.get("data_corrida")
        else "Data atual"
    )

    resumo = (
        "📋 *Resumo do treino*\n\n"
        f"⏱ Tempo: {tempo_formatado}\n"
        f"📏 Distância: {distancia_formatada}\n"
        f"⚡ Pace: {pace_formatado}\n"
        f"👟 Passos: {dados['passos']}\n"
        f"🔥 Calorias: {dados['calorias']}\n"
        f"🏷 Tipo: {dados['tipo_treino']}\n"
        f"📍 Local: {dados['local_treino']}\n"
        f"📅 Data: {data_info}\n\n"
        "Confirmar registro?"
    )


    bot.send_message(
        chat_id,
        resumo,
        reply_markup=teclado_confirmacao(),
        parse_mode="Markdown"
    )


def confirmar_registro(bot, services, chat_id):

    log = services["log"]
    corrida_service = services["corrida"]
    dados = registro_temp.get(chat_id)

    if not dados:
        bot.send_message(chat_id, "❌ Sessão expirada.")
        return

    try:
        corrida_service.registrar_corrida(
            telegram_id=chat_id,
            tempo_segundos=dados["tempo_segundos"],
            distancia_metros=dados["distancia_metros"],
            passos=dados["passos"],
            calorias=dados["calorias"],
            tipo_treino=dados["tipo_treino"],
            local_treino=dados["local_treino"],
            pace_segundos=dados.get("pace_segundos"),
            data_corrida=dados.get("data_corrida")
        )

        bot.send_message(chat_id, "✅ Corrida registrada com sucesso!")

        log.info(
            "CORRIDA REGISTRADA",
            extra={
                "telegram_id": chat_id,
                "correlation_id": dados["correlation_id"],
            },
        )

    except Exception:
        log.exception("Erro ao registrar corrida")
        bot.send_message(chat_id, "❌ Erro ao registrar corrida.")

    finally:
        limpar_sessao(chat_id)