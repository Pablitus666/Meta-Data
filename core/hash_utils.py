import hashlib
import os

class HashCalculator:
    """
    Genera firmas criptográficas (Hashes) para cadena de custodia forense.
    Calcula MD5, SHA-1 y SHA-256 de forma eficiente por bloques.
    """

    @staticmethod
    def calculate_hashes(filepath: str) -> dict:
        """
        Calcula hashes MD5, SHA1 y SHA256 del archivo.
        Retorna un diccionario con los resultados.
        """
        hashes = {
            "MD5": hashlib.md5(),
            "SHA-1": hashlib.sha1(),
            "SHA-256": hashlib.sha256()
        }

        try:
            with open(filepath, "rb") as f:
                # Leer en bloques de 64KB para no saturar memoria en archivos grandes
                while chunk := f.read(65536):
                    for h in hashes.values():
                        h.update(chunk)
            
            return {name: h.hexdigest().upper() for name, h in hashes.items()}
        except Exception as e:
            return {"Error": f"Hash calc failed: {str(e)}"}
