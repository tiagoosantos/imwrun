from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def menu_principal():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🏃 Registrar treino", callback_data="cmd_registrar"),
        InlineKeyboardButton("⏱ Calcular pace", callback_data="cmd_pace"),
        InlineKeyboardButton("🏆 Ranking por KM", callback_data="cmd_ranking_km"),
        InlineKeyboardButton("🏆 Ranking por Tempo", callback_data="cmd_ranking_tempo"),
        InlineKeyboardButton("📄 Relatório mensal", callback_data="cmd_relatorio"),
    )
    return markup
