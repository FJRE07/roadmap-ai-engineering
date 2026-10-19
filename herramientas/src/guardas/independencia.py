"""Guarda de independencia: solo se leen rutas públicas de otros departamentos (spec §1.3)."""

import re
import sys
from fnmatch import fnmatchcase
from pathlib import Path

import yaml

from guardas.departamentos import DEPARTAMENTOS, raiz_repo

CARPETAS_IGNORADAS = frozenset({"node_modules", ".venv", "dist", ".astro"})
ARCHIVOS_IGNORADOS = frozenset({"uv.lock", "pnpm-lock.yaml"})

REFERENCIA = re.compile(
    r"(?:\.\./)+(contratos|lecciones|sitio|reels|servicio|infra|bitacora|herramientas)/([\w./*-]*)"
)
CONTRATO = re.compile(r"(?:ejemplos/([^/]+)(?:/.*)?|([^/]+)\.(?:schema|tokens)\.json)")


def _leer_departamento(carpeta: Path) -> tuple[list[str], list[str]]:
    """Regresa ``(publica, consume)``; vacíos si no hay ``departamento.yaml``."""
    archivo = carpeta / "departamento.yaml"
    if not archivo.is_file():
        return [], []
    datos = yaml.safe_load(archivo.read_text(encoding="utf-8")) or {}
    return list(datos.get("publica") or []), list(datos.get("consume") or [])


def _es_publica(ruta: str, publica: list[str]) -> bool:
    if ruta == "departamento.yaml":
        return True
    for glob in publica:
        if fnmatchcase(ruta, glob):
            return True
        if glob.endswith("/**") and ruta == glob.removesuffix("/**"):
            return True
    return False


def _archivos_de_texto(carpeta: Path):
    """Recorre ``carpeta`` y produce ``(ruta, texto)`` de cada archivo UTF-8 no ignorado."""
    for ruta in sorted(carpeta.rglob("*")):
        relativa = ruta.relative_to(carpeta)
        if not ruta.is_file() or ruta.name in ARCHIVOS_IGNORADOS:
            continue
        if CARPETAS_IGNORADAS.intersection(relativa.parts[:-1]):
            continue
        try:
            yield ruta, ruta.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue


def violaciones(raiz: Path) -> list[str]:
    """Regresa una línea por cada referencia que rompe la independencia."""
    existentes = [d for d in DEPARTAMENTOS if (raiz / d).is_dir()]
    declaraciones = {d: _leer_departamento(raiz / d) for d in existentes}
    errores: list[str] = []

    for propio in existentes:
        _, consume = declaraciones[propio]
        for archivo, texto in _archivos_de_texto(raiz / propio):
            nombre = archivo.relative_to(raiz).as_posix()
            for coincidencia in REFERENCIA.finditer(texto):
                destino, ruta = coincidencia.group(1), coincidencia.group(2).rstrip("/")
                if destino == propio:
                    continue

                if destino == "contratos":
                    if ruta == "ejemplos":
                        continue
                    contrato = CONTRATO.fullmatch(ruta)
                    if contrato:
                        c = contrato.group(1) or contrato.group(2)
                        if c not in consume:
                            errores.append(f"{nombre}: usa el contrato '{c}' sin declararlo en consume")
                        continue

                publica, _ = declaraciones.get(destino, ([], []))
                if not _es_publica(ruta, publica):
                    errores.append(f"{nombre}: referencia a '{destino}/{ruta}' que no es pública")

    return errores


def main() -> int:
    errores = violaciones(raiz_repo())
    for error in errores:
        print(error)
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
