"""Guarda de alcance: un PR toca un solo departamento (spec §1.3, regla 4)."""

import argparse
import subprocess
import sys

from guardas.departamentos import PREFIJO_WORKFLOWS, dueno

AUTOR_DEPENDABOT = "dependabot[bot]"


def errores_alcance(rutas: list[str], autor: str) -> list[str]:
    """Regresa los errores de alcance de un PR; lista vacía si pasa."""
    if autor == AUTOR_DEPENDABOT and rutas and all(r.startswith(PREFIJO_WORKFLOWS) for r in rutas):
        return []

    duenos = sorted({dueno(ruta) for ruta in rutas})
    if len(duenos) <= 1:
        return []
    return [f"el PR toca varios departamentos: {', '.join(duenos)}"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Verifica que un PR toque un solo departamento.")
    parser.add_argument("--base", required=True, help="ref base del PR, p. ej. origin/main")
    parser.add_argument("--autor", required=True, help="login del autor del PR")
    args = parser.parse_args()

    salida = subprocess.run(
        ["git", "diff", "--name-only", f"{args.base}...HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    rutas = [linea for linea in salida.stdout.splitlines() if linea]

    errores = errores_alcance(rutas, args.autor)
    for error in errores:
        print(error)
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
