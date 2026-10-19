"""Pruebas de la guarda de independencia.

Cada prueba arma un repo falso en ``tmp_path`` con dos o tres departamentos.
Las rutas de referencia se construyen con ``"/".join([...])`` para que la
propia guarda no detecte este archivo como una violación.
"""

from pathlib import Path

import yaml
from guardas.independencia import violaciones


def _ref(*partes: str) -> str:
    return "/".join(partes)


def _departamento(
    raiz: Path,
    nombre: str,
    publica: list[str] | None = None,
    consume: list[str] | None = None,
    con_yaml: bool = True,
) -> Path:
    carpeta = raiz / nombre
    carpeta.mkdir()
    if con_yaml:
        datos = {"nombre": nombre, "publica": publica or [], "consume": consume or []}
        (carpeta / "departamento.yaml").write_text(yaml.safe_dump(datos), encoding="utf-8")
    return carpeta


def _archivo_con_referencia(carpeta: Path, nombre: str, referencia: str) -> None:
    destino = carpeta / nombre
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(f'leer("{referencia}")\n', encoding="utf-8")


def test_referencia_a_superficie_publica_pasa(tmp_path: Path):
    _departamento(tmp_path, "lecciones", publica=["contenido/**"])
    sitio = _departamento(tmp_path, "sitio")
    _archivo_con_referencia(sitio, "x.ts", _ref("..", "lecciones", "contenido", "L00.mdx"))

    assert violaciones(tmp_path) == []


def test_referencia_a_archivo_interno_falla(tmp_path: Path):
    _departamento(tmp_path, "lecciones", publica=["contenido/**"])
    sitio = _departamento(tmp_path, "sitio")
    interno = _ref("..", "lecciones", "src", "validador_lecciones", "reglas.py")
    _archivo_con_referencia(sitio, "x.ts", interno)

    errores = violaciones(tmp_path)

    assert len(errores) == 1
    assert _ref("sitio", "x.ts") in errores[0]
    assert _ref("lecciones", "src", "validador_lecciones", "reglas.py") in errores[0]


def test_contrato_declarado_pasa(tmp_path: Path):
    _departamento(tmp_path, "contratos")
    bitacora = _departamento(tmp_path, "bitacora", consume=["progreso.v1"])
    _archivo_con_referencia(bitacora, "x.py", _ref("..", "contratos", "progreso.v1.schema.json"))

    assert violaciones(tmp_path) == []


def test_contrato_no_declarado_falla(tmp_path: Path):
    _departamento(tmp_path, "contratos")
    bitacora = _departamento(tmp_path, "bitacora")
    _archivo_con_referencia(bitacora, "x.py", _ref("..", "contratos", "progreso.v1.schema.json"))

    errores = violaciones(tmp_path)

    assert len(errores) == 1
    assert _ref("bitacora", "x.py") in errores[0]
    assert "usa el contrato 'progreso.v1' sin declararlo en consume" in errores[0]


def test_autoreferencia_pasa(tmp_path: Path):
    _departamento(tmp_path, "lecciones")
    sitio = _departamento(tmp_path, "sitio")
    propio = _ref("..", "sitio", "src", "interno.ts")
    _archivo_con_referencia(sitio, _ref("src", "paginas", "a.ts"), propio)

    assert violaciones(tmp_path) == []


def test_departamento_yaml_siempre_es_publico(tmp_path: Path):
    _departamento(tmp_path, "lecciones", publica=[])
    sitio = _departamento(tmp_path, "sitio")
    _archivo_con_referencia(sitio, "x.ts", _ref("..", "lecciones", "departamento.yaml"))

    assert violaciones(tmp_path) == []


def test_sin_departamento_yaml_nada_es_publico(tmp_path: Path):
    _departamento(tmp_path, "lecciones", con_yaml=False)
    sitio = _departamento(tmp_path, "sitio")
    _archivo_con_referencia(sitio, "x.ts", _ref("..", "lecciones", "contenido", "L00.mdx"))

    errores = violaciones(tmp_path)

    assert len(errores) == 1
    assert _ref("sitio", "x.ts") in errores[0]
    assert "que no es pública" in errores[0]
