"""Guarda de binarios: nada de PDF ni EPUB en Git."""

import subprocess
import sys

from guardas.departamentos import raiz_repo

EXTENSIONES_PROHIBIDAS = (".pdf", ".epub")


def prohibidos(rutas: list[str]) -> list[str]:
    """Regresa, en el mismo orden, las rutas con extensión prohibida."""
    return [ruta for ruta in rutas if ruta.lower().endswith(EXTENSIONES_PROHIBIDAS)]


def main() -> int:
    salida = subprocess.run(
        ["git", "ls-files"], cwd=raiz_repo(), capture_output=True, text=True, check=True
    )
    rutas = [linea for linea in salida.stdout.splitlines() if linea]

    encontrados = prohibidos(rutas)
    for ruta in encontrados:
        print(f"{ruta}: archivo prohibido en Git")
    return 1 if encontrados else 0


if __name__ == "__main__":
    sys.exit(main())
