def convert_to_decimal(values, ref):
    """
    Convierte coordenadas GPS en formato DMS (Grados, Minutos, Segundos) a decimal.
    """
    try:
        degrees = float(values[0].num) / float(values[0].den)
        minutes = float(values[1].num) / float(values[1].den)
        seconds = float(values[2].num) / float(values[2].den)

        decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)

        if ref in ("S", "W"):
            decimal = -decimal

        return decimal
    except (IndexError, ZeroDivisionError, AttributeError):
        return None
