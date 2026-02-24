from datetime import datetime, date
import calendar
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


class CalendarBuilder:

    def __init__(
        self,
        min_date: date = None,
        max_date: date = None,
        start_hour: int = 5,
        end_hour: int = 22,
        interval_minutes: int = 30,
    ):
        self.min_date = min_date
        self.max_date = max_date
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.interval_minutes = interval_minutes

    # ===================================
    # CALENDÁRIO
    # ===================================

    def build_calendar(self, year: int, month: int):

        markup = InlineKeyboardMarkup(row_width=7)
        cal = calendar.monthcalendar(year, month)

        # Título
        markup.add(
            InlineKeyboardButton(
                f"{calendar.month_name[month]} {year}",
                callback_data="noop"
            )
        )

        # Dias da semana
        dias = ["S", "T", "Q", "Q", "S", "S", "D"]
        markup.add(*[InlineKeyboardButton(d, callback_data="noop") for d in dias])

        for semana in cal:
            linha = []

            for dia in semana:
                if dia == 0:
                    linha.append(InlineKeyboardButton(" ", callback_data="noop"))
                else:
                    data_dia = date(year, month, dia)

                    if self._is_disabled(data_dia):
                        linha.append(
                            InlineKeyboardButton(
                                f"🚫{dia}",
                                callback_data="noop"
                            )
                        )
                    else:
                        linha.append(
                            InlineKeyboardButton(
                                str(dia),
                                callback_data=f"cal_date_{year}_{month}_{dia}"
                            )
                        )

            markup.add(*linha)

        # Navegação
        markup.add(
            InlineKeyboardButton("⬅", callback_data=f"cal_prev_{year}_{month}"),
            InlineKeyboardButton("➡", callback_data=f"cal_next_{year}_{month}")
        )

        return markup

    # ===================================
    # HORÁRIO
    # ===================================

    def build_time_selector(self, selected_date: date):

        markup = InlineKeyboardMarkup(row_width=4)
        now = datetime.now()

        for hour in range(self.start_hour, self.end_hour + 1):
            for minute in range(0, 60, self.interval_minutes):

                dt = datetime(
                    selected_date.year,
                    selected_date.month,
                    selected_date.day,
                    hour,
                    minute
                )

                if self._is_time_disabled(dt, now):
                    continue

                markup.add(
                    InlineKeyboardButton(
                        f"{hour:02d}:{minute:02d}",
                        callback_data=f"cal_time_{hour}_{minute}"
                    )
                )

        return markup

    # ===================================
    # REGRAS
    # ===================================

    def _is_disabled(self, d: date):

        if self.min_date and d < self.min_date:
            return True

        if self.max_date and d > self.max_date:
            return True

        return False

    def _is_time_disabled(self, dt: datetime, now: datetime):

        if self.max_date and dt.date() > self.max_date:
            return True

        # Bloqueia horário futuro se for hoje
        if dt.date() == now.date() and dt > now:
            return True

        return False