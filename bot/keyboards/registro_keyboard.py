from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def teclado_tipo():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🚶 Caminhada", callback_data="tipo_caminhada"),
        InlineKeyboardButton("🏃 Corrida", callback_data="tipo_corrida"),
        InlineKeyboardButton("🏋 Outros", callback_data="tipo_outros"),
    )
    return markup

def teclado_local():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🌳 Rua", callback_data="local_rua"),
        InlineKeyboardButton("🏃 Esteira", callback_data="local_esteira"),
        InlineKeyboardButton("🏋 Máquinas", callback_data="local_maquinas"),
        InlineKeyboardButton("📍 Outros", callback_data="local_outros"),
    )
    return markup

def teclado_confirmacao():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("✅ Confirmar", callback_data="confirmar_registro"),
        InlineKeyboardButton("❌ Cancelar", callback_data="cancelar_registro"),
    )
    return markup
