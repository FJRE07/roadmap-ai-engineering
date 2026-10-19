# herramientas

Guardas que hacen cumplir las reglas del repositorio. Corren en CI en cada PR.

| Comando | Qué revisa |
|---|---|
| `guarda-alcance` | Que un PR toque un solo departamento |
| `guarda-independencia` | Que ningún departamento lea archivos internos de otro |
| `guarda-binarios` | Que no haya PDF ni EPUB en el repo |

Desde la raíz del repo: `uv run --project herramientas guarda-independencia`

`extraer-capitulo.sh <pdf> <inicio> <fin> <nombre>` saca a texto un rango de
páginas de un libro de `biblioteca/`.

Pruebas: `uv run pytest -q && uv run ruff check`
