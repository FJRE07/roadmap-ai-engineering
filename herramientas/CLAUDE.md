# Departamento herramientas

- Stack: Python ≥ 3.12 con uv. Código en `src/guardas/`, pruebas en `tests/`.
- Comandos: `uv run pytest -q`, `uv run ruff check`.
- No edites archivos fuera de `herramientas/`.
- En las pruebas, arma las rutas de ejemplo con `"/".join([...])` para que
  la guarda de independencia no se detecte a sí misma.
