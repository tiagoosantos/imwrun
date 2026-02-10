import csv
import os
from datetime import datetime
from threading import Lock
from telebot import types

csv_lock = Lock()


def configurar_monitoramento(bot):
    def log_to_csv(chat, user_id, content_type, text, message_id):
        chat_type = chat.type
        folder = "privates" if chat_type == "private" else "groups"
        name = chat.first_name if chat_type == "private" else chat.title

        base = os.path.join("chats", folder)
        os.makedirs(base, exist_ok=True)

        file_path = os.path.join(base, f"{chat.id}_{name}.csv")

        data = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "chat_id": chat.id,
            "chat_type": chat_type,
            "content_type": content_type,
            "text": text,
            "message_id": message_id,
        }

        with csv_lock:
            exists = os.path.exists(file_path)
            with open(file_path, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=data.keys())
                if not exists:
                    writer.writeheader()
                writer.writerow(data)

    def listener(updates):
        for u in updates:
            if isinstance(u, types.Message):
                log_to_csv(
                    u.chat,
                    u.from_user.id if u.from_user else None,
                    u.content_type,
                    u.text,
                    u.message_id,
                )

    bot.set_update_listener(listener)
