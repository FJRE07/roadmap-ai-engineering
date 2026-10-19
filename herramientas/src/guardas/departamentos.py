"""Departamentos del repo y a quién pertenece cada ruta (spec §1.2)."""

import subprocess
from pathlib import Path

DEPARTAMENTOS: tuple[str, ...] = (
    "contratos",
    "lecciones",
    "sitio",
    "reels",
    "servicio",
    "infra",
    "bitacora",
    "herramientas",
)

WORKFLOWS_ESPECIALES: dict[str, str] = {"guardas.yml": "herramientas", "pages.yml": "sitio"}

PREFIJO_WORKFLOWS = ".github/workflows/"


def dueno(ruta: str) -> str:
    """Regresa el departamento dueño de una ruta del repo, o ``"raiz"``."""
    if ruta.startswith(PREFIJO_WORKFLOWS):
        archivo = ruta.removeprefix(PREFIJO_WORKFLOWS)
        if archivo in WORKFLOWS_ESPECIALES:
            return WORKFLOWS_ESPECIALES[archivo]
        nombre = archivo.removesuffix(".yml")
        return nombre if nombre in DEPARTAMENTOS else "raiz"

    primera = ruta.split("/", 1)[0]
    return primera if primera in DEPARTAMENTOS else "raiz"


def raiz_repo() -> Path:
    """Raíz del repo git, para que las CLIs funcionen desde cualquier carpeta."""
    salida = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True
    )
    return Path(salida.stdout.strip())
