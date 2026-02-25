def usuario_cancelou(texto: str) -> bool:
    return texto.strip().lower() == "sair"

def parse_tempo(texto: str) -> int:
    texto = texto.strip().replace(".", ":").replace(",", ":").replace(" ", "")
    minutos, segundos = map(int, texto.split(":"))
    if segundos >= 60:
        raise ValueError
    return minutos * 60 + segundos

def parse_distancia(texto: str) -> int:
    texto = texto.strip().lower().replace(" ", "").replace(",", ".")
    if texto.isdigit():
        valor = int(texto)
        return valor * 1000 if valor < 100 else valor
    km_float = float(texto)
    if km_float <= 0:
        raise ValueError
    return int(km_float * 1000)

def formatar_tempo(segundos: int) -> str:
    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    segundos_restantes = segundos % 60
    
    if horas > 0:
        return f"{horas:02d}:{minutos:02d}:{segundos_restantes:02d}"
    
    return f"{minutos:02d}:{segundos_restantes:02d}"

def formatar_distancia(distancia_metros: int) -> str:
    km = distancia_metros / 1000
    return f"{km:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " km"
