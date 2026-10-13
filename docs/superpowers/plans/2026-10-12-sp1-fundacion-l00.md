# SP1 · Fundación (laboratorio L00) — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dejar publicado en GitHub Pages el roadmap como código: contratos versionados, departamento de lecciones con su validador, bitácora de avance, sitio Astro + Starlight con mapa y repasos, guardas de independencia en CI y la lección L00 escrita.

**Architecture:** Monorepo dividido en departamentos que no comparten código y solo se leen a través de archivos publicados que cumplen contratos JSON Schema en `contratos/`. Las herramientas de validación son proyectos Python independientes (uno por departamento, con uv); el sitio es un proyecto pnpm que adapta las lecciones al formato de Starlight en tiempo de build. Las guardas de CI hacen cumplir "sin código compartido" y "un PR, un departamento".

**Tech Stack:** Python ≥ 3.12 con uv 0.11 · jsonschema 4.26.0 · python-frontmatter 1.3.0 · PyYAML 6.0.3 · pytest 9.1.1 · ruff 0.17.0 · Node 24 LTS · pnpm 12.11.2 · Astro 7.3.8 · @astrojs/starlight 0.42.6 · zod vía `astro/zod` (Zod 4) · yaml 2.9.1 · vitest 5.0.4 · TypeScript 6.0.3 · @astrojs/check 0.9.10 · @fontsource/inter 5.3.0 · pre-commit 4.7.0 · GitHub Actions y GitHub Pages. Versiones verificadas en npm y PyPI el 2026-10-12.

**Spec:** `docs/superpowers/specs/2026-10-11-roadmap-ai-engineering-design.md` (revisión 3). Léela junto con este plan.

## Cómo se ejecuta este plan

- **Lo ejecutas tú con Claude Code**, una tarea a la vez, abriendo la sesión dentro de la carpeta del departamento de la tarea (`cd lecciones && claude`).
- Cada paso lleva una marca:
  - **[Tú]**: es objetivo de aprendizaje de L00. Lo escribes tú. A Claude Code solo le pides pistas (nivel 1, luego nivel 2) y la solución únicamente si la pides explícitamente. Anota en una libreta cuántas pistas abriste por paso: al final van a `bitacora/progreso.yaml`.
  - **[Claude Code]**: herramienta que no es objetivo de aprendizaje. Claude Code la genera; tú la revisas y debes poder explicar qué hace antes de hacer commit.
- **Flujo de PR (se repite en cada tarea desde la Tarea 2):**
  1. `git switch main && git pull`
  2. `git switch -c <rama-de-la-tarea>`
  3. Commits pequeños durante la tarea.
  4. `git push -u origin <rama-de-la-tarea>` y `gh pr create --fill`
  5. `gh pr checks --watch` hasta que todo esté en verde.
  6. `gh pr merge --squash --delete-branch`
  7. Si el PR cambió lo que el departamento publica, crea su tag de versión: `git switch main && git pull && git tag <depto>-v0.X.0 && git push --tags` (spec §1.3, punto 2).

## Global Constraints

- Un departamento nunca importa ni referencia archivos internos de otro; solo lee rutas declaradas en el `departamento.yaml` del otro y archivos de `contratos/` que declare en `consume`.
- Un PR toca un solo departamento; un cambio a `contratos/` va en su propio PR.
- Cada departamento tiene sus propias dependencias y archivo de bloqueo: pnpm por departamento, sin workspace compartido; uv para Python.
- Versiones exactas: `uv add paquete==X.Y.Z` y `.npmrc` con `save-exact=true`.
- Nada de PDF ni EPUB en Git; `biblioteca/` en `.gitignore`. Secretos nunca en Git; `.env` en `.gitignore`.
- Tipos de fuente: `oficial`, `paper`, `libro`, `estandar`, `apoyo`. Al menos una fuente por lección que no sea `apoyo`. `libro` exige `edicion` e `isbn` en el catálogo y `capitulo` en la cita.
- Componentes MDX permitidos: `Cita`, `Paso`, `Pista`, `Solucion`, `Comprobacion`, `Diagrama`.
- `objetivos`: de 2 a 4. Ids de lección `L` + dos dígitos, estables. `orden` admite decimales.
- Estados de avance: `pendiente`, `en_curso`, `lab_verificado`, `dominada`. `dominada` exige evidencia (`commit` o `captura`), `recuerdo.aciertos == 3` y `explicacion_60s == true`. `pistas`: `0`, `1`, `2` o `"solucion"` (vale 3 en el índice).
- Repasos a los 7 y a los 30 días de `fin`.
- Fuentes `oficial` y `apoyo` con más de 6 meses desde `verificado` se reportan como "por re-verificar" (aviso, no bloqueo).
- Estilo: fondo `#f1efe9`, negro `#111111`, rojo `#e3120b`, tipografía Inter, regla de 6 px.
- Sitio: `site: 'https://<USUARIO>.github.io'`, `base: '/roadmap-ai-engineering'`, en español.
- Claude no es fuente: toda afirmación técnica de una lección se respalda con una fuente citable, y las salidas esperadas se copian de una ejecución real.

## Review Focus

1. **Marcadores con `<` dentro de comandos** (`ssh root@<IP_SERVIDOR>`): el validador no debe confundirlos con componentes MDX cuando están en bloques o en código en línea. Prueba en la Tarea 4.
2. **Fechas sin comillas en YAML** (`fin: 2026-10-19`): PyYAML las convierte en objetos `date` y `format: date` de JSON Schema espera texto. Cada cargador Python las normaliza a ISO; pruebas en las Tareas 3, 4 y 5.
3. **Avance y lecciones desincronizados**: una lección sin registro en `progreso.yaml` se muestra como `pendiente`; un registro sin lección no rompe el build y se reporta. Prueba en la Tarea 6.
4. **`orden` decimal** (3.5): se ordena como número, no como texto. Prueba en la Tarea 6.
5. **Enlaces con `base`**: en GitHub Pages todo vive bajo `/roadmap-ai-engineering/`; los enlaces generados en páginas `.astro` usan `rutaLeccion()` con la base. Prueba en la Tarea 6.

---

### Task 1: Repositorio y raíz (commit directo a `main`, única excepción)

**Files:**
- Create: `README.md`, `CLAUDE.md`, `.gitignore`
- Create: `docs/superpowers/specs/2026-10-11-roadmap-ai-engineering-design.md` (la spec que te envié)
- Create: `docs/superpowers/plans/2026-10-12-sp1-fundacion-l00.md` (este plan)

**Interfaces:**
- Produces: la estructura raíz y las reglas que leen todas las sesiones de Claude Code.

- [ ] **Step 1 [Tú]: Crea el repo y clónalo**

Run: `gh repo create roadmap-ai-engineering --public --clone && cd roadmap-ai-engineering`
Expected: carpeta vacía con `.git/`.

- [ ] **Step 2 [Tú]: Copia la spec y el plan** a las rutas de arriba.

- [ ] **Step 3 [Tú]: Escribe `.gitignore`** con estas entradas: `biblioteca/`, `.env`, `.env.*`, `node_modules/`, `dist/`, `.astro/`, `__pycache__/`, `.venv/`, `.pytest_cache/`, `.ruff_cache/`, `sitio/src/content/docs/lecciones/`, `sitio/public/lecciones/`, `sitio/src/estilos/tokens.css`.

- [ ] **Step 4 [Tú]: Verifica que la biblioteca y los secretos quedan fuera**

Run: `mkdir -p biblioteca && touch biblioteca/x.pdf .env && git check-ignore -v biblioteca/x.pdf .env && rm -r biblioteca .env`
Expected: dos líneas que citan las reglas `biblioteca/` y `.env` de `.gitignore`.

- [ ] **Step 5 [Claude Code]: Redacta `CLAUDE.md` de la raíz; tú lo revisas.** Debe contener:
  1. La tabla de departamentos de la spec §1.2 (qué publica y qué consume cada uno).
  2. Las cinco reglas de independencia de §1.3, textuales.
  3. "Abre Claude Code dentro de la carpeta del departamento en que trabajas; no edites fuera de ella. Si necesitas cambiar un contrato, detente y propón un PR solo de `contratos/`."
  4. La regla de aprendizaje: en pasos marcados [Tú], dar solo la pista pedida (nivel 1 o 2) y la solución únicamente si se pide explícitamente.
  5. "Claude no es fuente" (spec §5.4) y "nada de PDF, EPUB ni secretos en Git".

- [ ] **Step 6 [Tú]: Escribe `README.md`**: qué es el proyecto (un párrafo), la estructura de carpetas y el enlace a la spec.

- [ ] **Step 7 [Tú]: Commit y push**

```bash
git add .
git commit -m "chore: estructura raíz, reglas y spec"
git push -u origin main
```

Expected: `gh repo view --web` muestra los archivos.

---

### Task 2: Guardas del repo (departamento `herramientas/`)

**Files:**
- Create: `herramientas/pyproject.toml`, `herramientas/uv.lock`, `herramientas/departamento.yaml`, `herramientas/CLAUDE.md`, `herramientas/README.md`
- Create: `herramientas/src/guardas/__init__.py`, `departamentos.py`, `alcance_pr.py`, `binarios.py`, `independencia.py`
- Create: `herramientas/extraer-capitulo.sh`
- Test: `herramientas/tests/test_departamentos.py`, `test_alcance_pr.py`, `test_binarios.py`, `test_independencia.py`
- Create: `.github/workflows/herramientas.yml`, `.github/workflows/guardas.yml`

**Interfaces:**
- Produces:
  - `DEPARTAMENTOS: tuple[str, ...] = ("contratos", "lecciones", "sitio", "reels", "servicio", "infra", "bitacora", "herramientas")`
  - `WORKFLOWS_ESPECIALES: dict[str, str] = {"guardas.yml": "herramientas", "pages.yml": "sitio"}`
  - `dueno(ruta: str) -> str`: el departamento dueño de una ruta del repo, o `"raiz"`. `.github/workflows/<x>.yml` pertenece a `x` si `x` es departamento, o al valor de `WORKFLOWS_ESPECIALES`.
  - `errores_alcance(rutas: list[str], autor: str) -> list[str]`
  - `prohibidos(rutas: list[str]) -> list[str]` con `EXTENSIONES_PROHIBIDAS = (".pdf", ".epub")`, sin distinguir mayúsculas.
  - `violaciones(raiz: Path) -> list[str]`
  - Formato de `departamento.yaml`, leído por las guardas:
    ```yaml
    nombre: lecciones
    publica: [contenido/**, fuentes/catalogo.yaml, fases.yaml]   # globs relativos al departamento
    consume: [leccion.v1]                                          # contratos usados
    ```
  - CLIs: `guarda-alcance --base <ref> --autor <login>`, `guarda-independencia`, `guarda-binarios`. Todas regresan 0 si pasa y 1 si falla, imprimiendo una línea por error.

**Reglas de `violaciones`** (el código lo escribe Claude Code; las reglas son la especificación):
- Recorre los archivos de texto de cada carpeta de departamento existente. Ignora `node_modules/`, `.venv/`, `dist/`, `.astro/`, `uv.lock`, `pnpm-lock.yaml` y archivos que no se decodifiquen como UTF-8.
- Detecta referencias con la expresión `(?:\.\./)+(contratos|lecciones|sitio|reels|servicio|infra|bitacora|herramientas)/([\w./*-]*)`.
- Una referencia al propio departamento siempre pasa. `departamento.yaml` de cualquier departamento siempre es público.
- Una referencia a `contratos/` pasa si apunta a `ejemplos/` (la carpeta), a `ejemplos/<c>/…`, a `<c>.schema.json` o a `<c>.tokens.json`, siempre que `<c>` esté en el `consume` propio. Si no, el error es `"<archivo>: usa el contrato '<c>' sin declararlo en consume"`.
- Una referencia a otro departamento pasa si la ruta (sin `/` final) coincide con algún glob de su `publica`, o si es la carpeta raíz de un glob (`contenido/` con `contenido/**`). Si no, el error es `"<archivo>: referencia a '<depto>/<ruta>' que no es pública"`.
- Si un departamento no tiene `departamento.yaml`, nada suyo es público y no consume nada.
- En las pruebas, las rutas de ejemplo se construyen con `"/".join([...])` para que la guarda no se detecte a sí misma.

- [ ] **Step 1 [Tú]: Crea el proyecto con uv**

```bash
uv init --package --name guardas herramientas
cd herramientas
uv add pyyaml==6.0.3
uv add --dev pytest==9.1.1 ruff==0.17.0
```

Declara los tres scripts en `[project.scripts]` de `pyproject.toml`: `guarda-alcance = "guardas.alcance_pr:main"`, `guarda-independencia = "guardas.independencia:main"`, `guarda-binarios = "guardas.binarios:main"`.

- [ ] **Step 2 [Claude Code]: Escribe las pruebas (fallan)**

```python
# tests/test_departamentos.py
def test_dueno_de_carpeta(): assert dueno("lecciones/fases.yaml") == "lecciones"
def test_dueno_de_workflow_por_nombre(): assert dueno(".github/workflows/sitio.yml") == "sitio"
def test_dueno_de_workflows_especiales():
    assert dueno(".github/workflows/guardas.yml") == "herramientas"
    assert dueno(".github/workflows/pages.yml") == "sitio"
def test_dueno_de_raiz():
    assert {dueno("README.md"), dueno("docs/x.md"), dueno(".github/dependabot.yml")} == {"raiz"}

# tests/test_alcance_pr.py
def test_un_departamento_con_su_workflow_pasa():
    assert errores_alcance(["lecciones/fases.yaml", ".github/workflows/lecciones.yml"], autor="jair") == []
def test_dos_departamentos_falla():
    errores = errores_alcance(["lecciones/a.mdx", "sitio/b.ts"], autor="jair")
    assert errores and "lecciones" in errores[0] and "sitio" in errores[0]
def test_contratos_con_otro_falla():
    assert errores_alcance(["contratos/a.json", "lecciones/b.mdx"], autor="jair")
def test_sin_cambios_pasa(): assert errores_alcance([], autor="jair") == []
def test_dependabot_solo_workflows_pasa():
    assert errores_alcance([".github/workflows/sitio.yml", ".github/workflows/lecciones.yml"], autor="dependabot[bot]") == []
def test_dependabot_con_otros_archivos_falla():
    assert errores_alcance(["sitio/package.json", ".github/workflows/lecciones.yml"], autor="dependabot[bot]")

# tests/test_binarios.py
def test_detecta_pdf_y_epub_sin_importar_mayusculas():
    assert prohibidos(["a/B.PDF", "c.epub", "notas.md"]) == ["a/B.PDF", "c.epub"]
```

Para `tests/test_independencia.py`, cada prueba arma un repo falso en `tmp_path` con dos o tres departamentos y sus `departamento.yaml`:
- `test_referencia_a_superficie_publica_pasa`: `sitio/x.ts` con `"../lecciones/contenido/L00.mdx"` y `lecciones` publica `contenido/**` → `[]`.
- `test_referencia_a_archivo_interno_falla`: `sitio/x.ts` con `"../lecciones/src/validador_lecciones/reglas.py"` → un error que contiene `sitio/x.ts` y `lecciones/src/validador_lecciones/reglas.py`.
- `test_contrato_declarado_pasa` y `test_contrato_no_declarado_falla`: `bitacora/x.py` con `"../contratos/progreso.v1.schema.json"`, con y sin `progreso.v1` en `consume`.
- `test_autoreferencia_pasa`, `test_departamento_yaml_siempre_es_publico` y `test_sin_departamento_yaml_nada_es_publico`.

- [ ] **Step 3 [Tú]: Verifica que fallan**

Run: `uv run pytest -q`
Expected: FAIL (`ModuleNotFoundError` o funciones sin definir).

- [ ] **Step 4 [Claude Code]: Implementa** `departamentos.py`, `alcance_pr.py`, `binarios.py` e `independencia.py` con las interfaces de arriba. `alcance_pr.main` obtiene los cambios con `git diff --name-only <base>...HEAD`; `binarios.main` usa `git ls-files`. Regla de dependabot: si `autor == "dependabot[bot]"` y todas las rutas están bajo `.github/workflows/`, pasa.

- [ ] **Step 5 [Tú]: Verifica que pasan**

Run: `uv run pytest -q && uv run ruff check`
Expected: todas las pruebas en verde y `All checks passed!`.

- [ ] **Step 6 [Claude Code]: Escribe `extraer-capitulo.sh`.** Uso: `extraer-capitulo.sh <pdf> <pagina_inicio> <pagina_fin> <nombre_salida>`. Ejecuta `pdftotext -layout -f <inicio> -l <fin>` y escribe en `biblioteca/.extraido/<nombre_salida>.txt`. Valida que lleguen 4 argumentos y que exista `pdftotext`.

Run: `shellcheck extraer-capitulo.sh`
Expected: sin salida.

- [ ] **Step 7 [Tú]: Escribe `departamento.yaml`** (`nombre: herramientas`, `publica: []`, `consume: []`), `README.md` (qué hace cada guarda y cómo correrla) y `CLAUDE.md` (stack, comandos `uv run pytest`, `uv run ruff check`, y "no edites fuera de `herramientas/`").

- [ ] **Step 8 [Tú]: Escribe los workflows**
  - `.github/workflows/herramientas.yml`: en `pull_request` y `push` a `main` con `paths: [herramientas/**, .github/workflows/herramientas.yml, .github/workflows/guardas.yml]`. Instala uv con `astral-sh/setup-uv` y corre `uv sync`, `uv run ruff check` y `uv run pytest` con `working-directory: herramientas`.
  - `.github/workflows/guardas.yml`: en todo `pull_request` y en `push` a `main`. Usa `actions/checkout@v7` con `fetch-depth: 0`. En un job llamado **`guardas`** (es el check que la Tarea 9 hará obligatorio), corre `guarda-alcance --base origin/${{ github.base_ref }} --autor ${{ github.event.pull_request.user.login }}` (solo en PR), `guarda-independencia` y `guarda-binarios` con `uv run --project herramientas`, y `gitleaks/gitleaks-action`.
  - Para las acciones sin versión en este plan, usa la versión mayor que indique su README hoy. Dependabot las mantendrá (Tarea 9).

- [ ] **Step 9 [Tú]: Abre el PR** (rama `herramientas/guardas`) según el flujo y verifica en `gh pr checks` que corren `herramientas` y `guardas` en verde.

---

### Task 3: Contratos v1 (departamento `contratos/`)

**Files:**
- Create: `contratos/leccion.v1.schema.json`, `contratos/progreso.v1.schema.json`, `contratos/estilo.v1.schema.json`, `contratos/estilo.v1.tokens.json`
- Create: `contratos/ejemplos/<contrato>/<definicion>/{validos,invalidos}/*.yaml`
- Create: `contratos/README.md`, `contratos/CLAUDE.md`, `contratos/departamento.yaml`
- Create: `contratos/pyproject.toml`, `contratos/uv.lock`, `contratos/src/validador_contratos/{__init__,carga,cli}.py`
- Test: `contratos/tests/test_cli.py`
- Create: `.github/workflows/contratos.yml`

**Interfaces:**
- Produces:
  - `leccion.v1.schema.json` (JSON Schema 2020-12) con `$defs`: `fuenteCatalogo`, `catalogo`, `fase`, `fases`, `citaFuente`, `leccion`. La raíz es `{"$ref": "#/$defs/leccion"}`.
  - `progreso.v1.schema.json`; `estilo.v1.schema.json` y `estilo.v1.tokens.json`.
  - Convención de ejemplos: `ejemplos/<contrato>/<definicion>/…`, donde `<definicion>` es un `$def` o `raiz` (el esquema completo).
  - `cargar_yaml(ruta: Path) -> Any`: carga YAML y convierte `date` y `datetime` a texto ISO, de forma recursiva.
  - `validar(raiz: Path) -> list[str]` y CLI `validar-contratos [--raiz .]`: imprime un error por línea y regresa 1, o imprime `0 errores` y regresa 0.

**Restricciones de `leccion.v1`** (todas las definiciones con `additionalProperties: false`):
- `fuenteCatalogo`. Requeridos: `id` (`^[a-z0-9-]+$`), `titulo` (minLength 1), `url` (`format: uri`), `tipo` (enum de los 5 tipos), `verificado` (`format: date`). Opcionales: `autores` (lista de texto), `edicion`, `isbn` (`^[0-9X-]{10,17}$`), `archivo_local` (`^[^/]+\.pdf$`). Si `tipo` es `libro`, `edicion` e `isbn` son requeridos (`if`/`then`).
- `catalogo`: `{fuentes: [fuenteCatalogo], minItems 1}`.
- `fase`. Requeridos: `numero` (entero ≥ 1), `prefijo` (`^[A-Z]{2}$`), `titulo`, `semanas` (número > 0), `hito`, `lecturas` (lista de ids).
- `fases`: `{fases: [fase], minItems 1}`.
- `citaFuente`: `id` requerido; `capitulo` y `paginas` opcionales.
- `leccion`. Requeridos:
  - `id`: `^L\d{2}$`.
  - `titulo`.
  - `fase`: entero ≥ 1.
  - `orden`: número > 0.
  - `duracion`: `{lectura_min` entero ≥ 1, `laboratorio_h` número > 0`}`.
  - `prerequisitos`: lista de ids.
  - `objetivos`: de 2 a 4 textos.
  - `fuentes`: lista de `citaFuente`, mínimo 1.
  - `laboratorio`: `{objetivo, entregable (commit|servicio|captura), verificacion {comando, salida_esperada, entorno}}`.
  - `reel`: `{tema, analogia, gancho {texto, ancla}, idea {texto, ancla}, ejemplo {texto, ancla}, cierre {texto}, fuentes (lista de ids, mínimo 1)}`.

**Restricciones de `progreso.v1`:**
- Raíz: `lecciones` es un objeto con `patternProperties` `^L\d{2}$` y `additionalProperties: false`; `mejoras` es una lista opcional.
- Registro:
  - `estado`: enum de los 4 estados, requerido.
  - `inicio` y `fin`: `format: date`.
  - `horas`: número ≥ 0.
  - `pistas`: lista con elementos en `enum: [0, 1, 2, "solucion"]`.
  - `evidencia`: `{commit` `^[0-9a-f]{7,40}$`, `captura` `^evidencias/.+\.(png|jpg|jpeg|webp)$`, `url` y `reel` (`format: uri`)`}`.
  - `recuerdo`: `{fecha (date), aciertos (entero 0 a 3)}`.
  - `explicacion_60s`: booleano.
- Condicionales:
  - Si `estado` es `lab_verificado` o `dominada`, `evidencia` debe tener `commit` o `captura`.
  - Si `estado` es `dominada`, además son requeridos `fin`, `recuerdo` con `aciertos` `const: 3` y `explicacion_60s` `const: true`.
- `mejora`: requeridos `fecha`, `que` y `por_que`; `evidencia` opcional (misma forma).

**`estilo.v1.tokens.json`:** `{"color": {"fondo": "#f1efe9", "negro": "#111111", "rojo": "#e3120b"}, "tipografia": {"familia": "Inter", "pesos": [400, 500, 800, 900]}, "medida": {"regla_px": 6}}`. Su esquema exige esas claves; los colores con patrón `^#[0-9a-f]{6}$`.

- [ ] **Step 1 [Tú]: Escribe `leccion.v1.schema.json`** con las restricciones de arriba.

- [ ] **Step 2 [Tú]: Escribe los ejemplos de `leccion.v1`**
  - `leccion/validos/completa.yaml`
  - `leccion/invalidos/`: `un-objetivo.yaml`, `id-mal-formado.yaml` (`id: L3`), `entregable-desconocido.yaml`, `campo-extra.yaml`
  - `catalogo/validos/catalogo.yaml`
  - `catalogo/invalidos/`: `libro-sin-isbn.yaml`, `tipo-desconocido.yaml`
  - `fases/validos/fases.yaml` y `fases/invalidos/prefijo-minusculas.yaml`
  - Escribe las fechas **sin comillas** (`verificado: 2026-10-12`).

- [ ] **Step 3 [Tú]: Crea el proyecto del validador**

```bash
uv init --package --name validador-contratos contratos
cd contratos && uv add "jsonschema[format-nongpl]==4.26.0" pyyaml==6.0.3 && uv add --dev pytest==9.1.1 ruff==0.17.0
```

Script: `validar-contratos = "validador_contratos.cli:main"`.

- [ ] **Step 4 [Claude Code]: Escribe las pruebas (fallan)**, cada una armando un mini contrato en `tmp_path`:
  - `test_valido_que_no_cumple_se_reporta`: un ejemplo en `validos/` que viola el esquema → el error contiene la ruta del ejemplo.
  - `test_invalido_que_cumple_se_reporta`.
  - `test_esquema_mal_formado_se_reporta` (`"type": "texto"`).
  - `test_fecha_sin_comillas_cumple_format_date`: `{"type": "string", "format": "date"}` contra un YAML con `fecha: 2026-10-19` → `[]`.
  - `test_repositorio_real_sin_errores`: `validar(Path(__file__).parents[1]) == []`.

- [ ] **Step 5 [Tú]: Verifica que fallan.** Run: `uv run pytest -q`. Expected: FAIL.

- [ ] **Step 6 [Claude Code]: Implementa** `carga.py` y `cli.py`:
  - Usa `Draft202012Validator.check_schema` para cada `*.schema.json`.
  - Valida con `FormatChecker()`, para que `format` se aplique.
  - Valida `estilo.v1.tokens.json` contra `estilo.v1.schema.json`.

- [ ] **Step 7 [Tú]: Verifica que pasan.** Run: `uv run pytest -q && uv run validar-contratos`. Expected: pruebas en verde y `0 errores`.

- [ ] **Step 8 [Tú]: Escribe `progreso.v1.schema.json` y sus ejemplos**
  - `raiz/validos/`: `en-curso.yaml`, `dominada.yaml`
  - `raiz/invalidos/`: `dominada-sin-recuerdo.yaml`, `dominada-dos-aciertos.yaml`, `lab-verificado-sin-evidencia.yaml`, `pista-invalida.yaml` (un `4`), `id-mal-formado.yaml`
  - Después, `estilo.v1.schema.json` y `estilo.v1.tokens.json`.

Run: `uv run validar-contratos`
Expected: `0 errores`.

- [ ] **Step 9 [Tú]: Escribe `contratos/README.md`** con:
  1. La lista de contratos y quién los produce y consume (§1.2).
  2. Las reglas de versión de §1.3, punto 3.
  3. El contrato de componentes MDX: `Cita {id}`, `Paso {n, titulo}`, `Pista {nivel: 1|2}`, `Solucion {}`, `Comprobacion {comando, salida}` y `Diagrama {src, alt, pie?}`. `src` es relativo a `lecciones/contenido/`.
  4. Las reglas semánticas que el esquema no expresa y que valida el productor (`lecciones/`): ids de fuente existentes, al menos una fuente que no sea `apoyo`, capítulo en citas de libro, citas declaradas y usadas, componentes permitidos y nombre de archivo que empieza con el id.

  Agrega `departamento.yaml` (`nombre: contratos`, `publica: ["*.schema.json", "*.tokens.json", "ejemplos/**"]`, `consume: []`) y `CLAUDE.md`.

- [ ] **Step 10 [Tú]: Escribe `.github/workflows/contratos.yml`** (paths `contratos/**` y el propio workflow): `uv sync`, `uv run ruff check`, `uv run pytest` y `uv run validar-contratos`.

- [ ] **Step 11 [Tú]: Abre el PR** (rama `contratos/v1`). Verifica que este PR toca solo `contratos/` y su workflow.

---

### Task 4: Validador, catálogo y fases (departamento `lecciones/`)

**Files:**
- Create: `lecciones/pyproject.toml`, `uv.lock`, `src/validador_lecciones/{__init__,carga,reglas,cli}.py`
- Test: `lecciones/tests/test_reglas.py`, `lecciones/tests/test_cli.py`, `lecciones/tests/datos/{ok,mal}/…`
- Create: `lecciones/fuentes/catalogo.yaml`, `lecciones/fases.yaml`, `lecciones/contenido/.gitkeep`, `lecciones/contenido/diagramas/.gitkeep`
- Create: `lecciones/departamento.yaml`, `CLAUDE.md`, `README.md`
- Create: `.github/workflows/lecciones.yml`

**Interfaces:**
- Consumes: `contratos/leccion.v1.schema.json` (Tarea 3).
- Produces:
  - `COMPONENTES_PERMITIDOS = {"Cita", "Paso", "Pista", "Solucion", "Comprobacion", "Diagrama"}`
  - `cargar_yaml(ruta: Path) -> Any` (fechas a ISO) y `leer_leccion(ruta: Path) -> tuple[dict, str]` (metadatos normalizados y cuerpo).
  - `sin_codigo(cuerpo: str) -> str`: quita bloques con ``` o ~~~ y código en línea.
  - `componentes_usados(cuerpo: str) -> set[str]`: etiquetas `<Nombre` en PascalCase fuera de código.
  - `citas_usadas(cuerpo: str) -> list[str]`: ids de `<Cita id="…"` fuera de código.
  - `errores_esquema(datos: dict, esquema: dict, definicion: str) -> list[str]`
  - `errores_catalogo(catalogo: dict) -> list[str]`: ids únicos.
  - `errores_fases(fases: dict, catalogo: dict) -> list[str]`: números y prefijos únicos; lecturas existentes en el catálogo.
  - `errores_leccion(ruta: Path, meta: dict, cuerpo: str, catalogo: dict, fases: dict) -> list[str]`: las reglas semánticas de `contratos/README.md`.
  - `errores_conjunto(lecciones: list[dict]) -> list[str]`: ids únicos, prerequisitos existentes y pares `(fase, orden)` únicos.
  - `fuentes_caducadas(catalogo: dict, hoy: date, meses: int = 6) -> list[str]`: ids `oficial` o `apoyo` con `verificado` anterior a `hoy` menos `meses`.
  - CLI `validar-lecciones [--raiz .] [--contratos ../contratos] [--caducadas]`: imprime `<archivo>: <mensaje>` por error y regresa 1, o imprime `0 errores` y regresa 0; con `--caducadas` lista las fuentes por re-verificar y regresa 0.

- [ ] **Step 1 [Tú]: Crea el proyecto**

```bash
uv init --package --name validador-lecciones lecciones
cd lecciones && uv add "jsonschema[format-nongpl]==4.26.0" python-frontmatter==1.3.0 pyyaml==6.0.3 && uv add --dev pytest==9.1.1 ruff==0.17.0
```

Script: `validar-lecciones = "validador_lecciones.cli:main"`.

- [ ] **Step 2 [Claude Code]: Escribe las pruebas (fallan)** en `tests/test_reglas.py`, con un catálogo de prueba `{a: oficial, b: libro, c: apoyo}` y fases `[{numero: 1, …}]`:
  - `test_cita_no_declarada_falla`: fuentes `[a]`, cuerpo con `<Cita id="b" />` → un error contiene `"b"`.
  - `test_fuente_declarada_sin_citar_falla`.
  - `test_solo_fuentes_apoyo_falla` (fuentes `[c]`).
  - `test_libro_sin_capitulo_falla` (fuentes `[{id: b}]`).
  - `test_reel_con_fuente_no_declarada_falla`.
  - `test_componente_no_permitido_falla`: `<Tabs>` → un error contiene `"Tabs"`.
  - `test_marcadores_en_codigo_se_ignoran`: un bloque con `ssh root@<IP_SERVIDOR>` y código en línea con `<NODO_GPU>` → ningún error de componente.
  - `test_nombre_de_archivo_debe_empezar_con_id`: `L01-x.mdx` con `id: L00` → error.
  - `test_fase_inexistente_falla`.
  - `test_ids_duplicados_falla` y `test_prerequisito_inexistente_falla` (`errores_conjunto`).
  - `test_lecturas_de_fase_deben_existir_en_catalogo`.
  - `test_ids_de_catalogo_duplicados_falla`.
  - `test_fuentes_caducadas`: `oficial` verificado `2026-01-01`, `libro` `2020-01-01`, `hoy=date(2026, 10, 12)` → solo el id oficial.

  En `tests/test_cli.py`: `test_cli_ok` (`main(["--raiz", "tests/datos/ok", "--contratos", "../contratos"]) == 0`), `test_cli_mal` (`== 1` y la salida nombra el archivo) y `test_repositorio_real`.

- [ ] **Step 3 [Tú]: Verifica que fallan.** Run: `uv run pytest -q`. Expected: FAIL.

- [ ] **Step 4 [Claude Code]: Implementa** `carga.py`, `reglas.py` y `cli.py` con las firmas de arriba. `leer_leccion` usa python-frontmatter y normaliza fechas igual que `cargar_yaml`.

- [ ] **Step 5 [Tú]: Verifica que pasan.** Run: `uv run pytest -q && uv run ruff check`. Expected: verde.

- [ ] **Step 6 [Tú]: Escribe `fuentes/catalogo.yaml`** con los 13 libros de la spec §3.1. Ids:
  - `how-linux-works-3e`, `docker-up-running-3e`, `pro-git-2e`
  - `fundamentals-data-engineering`, `ddia-2e`
  - `designing-ml-systems`, `hands-on-ml-sklearn-pytorch`
  - `ai-engineering`, `hands-on-llms`, `llm-from-scratch`
  - `terraform-up-running-3e`, `sre-google`, `linux-command-line`

  Copia título, autores, edición e ISBN de la **página oficial de cada edición**. Usa las URLs de §10 de la spec donde existan. Pon como `verificado` la fecha en que lo revisas. Cada dato que copies lo verificas tú: es la política de fuentes en práctica.

- [ ] **Step 7 [Tú]: Escribe `fases.yaml`** con las 6 fases de la spec §3. Para cada una: `numero`, `prefijo` (HL, DT, ML, IA, CL, PR), `titulo`, `semanas` (4, 4, 5, 6, 5, 3), `hito` (la columna "Hito") y `lecturas` (los ids de §3.1; la fase 6 usa `ddia-2e` y `ai-engineering`).

Run: `uv run validar-lecciones`
Expected: `0 errores` (aún no hay lecciones).

- [ ] **Step 8 [Tú]: Escribe `departamento.yaml`** (`nombre: lecciones`, `publica: [contenido/**, fuentes/catalogo.yaml, fases.yaml]`, `consume: [leccion.v1]`), `README.md` (cómo crear una lección y validarla) y `CLAUDE.md` (estructura de lección de la spec §2.2, componentes permitidos, "Claude no es fuente", comandos).

- [ ] **Step 9 [Tú]: Escribe `.github/workflows/lecciones.yml`**
  - **Job `validar`**: en PR y push con `paths: [lecciones/**, contratos/**, .github/workflows/lecciones.yml]`. Corre `uv sync`, `ruff check`, `pytest` y `validar-lecciones`.
  - **Job `salud-fuentes`**: con `schedule` semanal (`cron: "0 14 * * 1"`) y `workflow_dispatch`, con `permissions: issues: write`. Corre `lycheeverse/lychee-action` sobre `lecciones/**/*.mdx` y `lecciones/fuentes/catalogo.yaml`, y `validar-lecciones --caducadas`. Si alguno reporta algo, crea un issue con `gh issue create --title "Fuentes por revisar" --body-file reporte.md`.

- [ ] **Step 10 [Tú]: Abre el PR** (rama `lecciones/validador`).

---

### Task 5: Bitácora de avance (departamento `bitacora/`)

**Files:**
- Create: `bitacora/pyproject.toml`, `uv.lock`, `src/validador_progreso/{__init__,carga,cli}.py`
- Test: `bitacora/tests/test_cli.py`
- Create: `bitacora/progreso.yaml`, `bitacora/ideas.md`, `bitacora/evidencias/.gitkeep`
- Create: `bitacora/departamento.yaml`, `CLAUDE.md`
- Create: `.github/workflows/bitacora.yml`

**Interfaces:**
- Consumes: `contratos/progreso.v1.schema.json`.
- Produces:
  - `errores_progreso(datos: dict, esquema: dict, raiz_bitacora: Path) -> list[str]`: el esquema más la existencia de cada `captura` en disco.
  - CLI `validar-progreso [--raiz .] [--contratos ../contratos]`: misma salida que `validar-lecciones` (`0 errores` si pasa).
  - `progreso.yaml`, publicado para `sitio/`.

- [ ] **Step 1 [Tú]: Crea el proyecto**

```bash
uv init --package --name validador-progreso bitacora
cd bitacora && uv add "jsonschema[format-nongpl]==4.26.0" pyyaml==6.0.3 && uv add --dev pytest==9.1.1 ruff==0.17.0
```

Script: `validar-progreso = "validador_progreso.cli:main"`.

- [ ] **Step 2 [Claude Code]: Escribe las pruebas (fallan)**
  - `test_progreso_valido_pasa`
  - `test_dominada_sin_explicacion_falla`
  - `test_captura_inexistente_falla`: `captura: evidencias/no-existe.png` → error con esa ruta.
  - `test_fechas_sin_comillas_pasan`
  - `test_repositorio_real`

- [ ] **Step 3 [Tú]: Verifica que fallan** (`uv run pytest -q`).

- [ ] **Step 4 [Claude Code]: Implementa** `carga.py` (con su propio `cargar_yaml`, que normaliza fechas; se duplica a propósito, no se comparte) y `cli.py`.

- [ ] **Step 5 [Tú]: Verifica que pasan** (`uv run pytest -q && uv run ruff check`).

- [ ] **Step 6 [Tú]: Escribe `progreso.yaml` inicial**: `lecciones: {L00: {estado: en_curso, inicio: <fecha en que empezaste la Tarea 1>, pistas: []}}` y `mejoras: []`. Escribe también `ideas.md` (vacío con un título) y `evidencias/.gitkeep`.

Run: `uv run validar-progreso`
Expected: `0 errores`.

- [ ] **Step 7 [Tú]: Escribe `departamento.yaml`** (`nombre: bitacora`, `publica: [progreso.yaml, evidencias/**]`, `consume: [progreso.v1]`), `CLAUDE.md` (qué significa cada estado y la regla de evidencia duradera de la spec §3.3) y `.github/workflows/bitacora.yml` (paths `bitacora/**` y `contratos/**`: `uv sync`, `pytest` y `validar-progreso`).

- [ ] **Step 8 [Tú]: Abre el PR** (rama `bitacora/inicio`).

---

### Task 6: Sitio — esquemas, pruebas de contrato y lógica (departamento `sitio/`)

**Files:**
- Create: `sitio/package.json`, `pnpm-lock.yaml`, `.npmrc`, `.node-version`, `tsconfig.json`, `astro.config.ts`
- Create: `sitio/src/content.config.ts`, `sitio/src/content/docs/index.mdx`
- Create: `sitio/src/esquemas/{catalogo,fases,leccion,progreso}.ts`
- Create: `sitio/src/datos/{rutas,cargar}.ts`, `sitio/src/logica/{progreso,repasos,rutas}.ts`
- Test: `sitio/tests/{contratos,progreso,repasos,rutas,cargar}.test.ts`, `sitio/tests/datos/*.yaml`
- Create: `sitio/departamento.yaml`, `CLAUDE.md`, `README.md`
- Create: `.github/workflows/sitio.yml`

**Interfaces:**
- Consumes:
  - `contratos/ejemplos/{leccion.v1,progreso.v1}/…` (pruebas de contrato) y `contratos/estilo.v1.tokens.json`.
  - `lecciones/fuentes/catalogo.yaml`, `lecciones/fases.yaml` y `bitacora/progreso.yaml`.
- Produces:
  - `src/esquemas/*.ts`, todos con `import { z } from 'astro/zod'`:
    - `fuenteCatalogoSchema`, `catalogoSchema` → tipos `FuenteCatalogo`, `Catalogo`.
    - `faseSchema`, `fasesSchema` → tipo `Fase`.
    - `leccionSchema` → tipo `Leccion`.
    - `progresoSchema` → tipos `Progreso`, `RegistroLeccion` y `EstadoLeccion = "pendiente" | "en_curso" | "lab_verificado" | "dominada"`.
    - Reflejan los contratos completos, incluidos los condicionales (`superRefine`). Las fechas usan `z.iso.date()`.
  - `src/datos/rutas.ts`: **todas** las rutas a otros departamentos viven aquí, como literales relativos:
    - `RUTA_CONTENIDO = new URL('../../../lecciones/contenido/', import.meta.url)`
    - `RUTA_CATALOGO = new URL('../../../lecciones/fuentes/catalogo.yaml', import.meta.url)`
    - `RUTA_FASES = new URL('../../../lecciones/fases.yaml', import.meta.url)`
    - `RUTA_PROGRESO = new URL('../../../bitacora/progreso.yaml', import.meta.url)`
    - `RUTA_TOKENS = new URL('../../../contratos/estilo.v1.tokens.json', import.meta.url)`
  - `src/datos/cargar.ts`:
    - `cargarCatalogo(ruta: URL = RUTA_CATALOGO): Promise<Catalogo>`
    - `cargarFases(ruta: URL = RUTA_FASES): Promise<Fase[]>`
    - `cargarProgreso(ruta: URL = RUTA_PROGRESO): Promise<Progreso>`
    - Parsean con `yaml.parse` (esquema core: las fechas quedan como texto) y validan. Ante un error lanzan `Error` cuyo mensaje empieza con la ruta del archivo.
  - `src/logica/progreso.ts`:
    - `estadoDe(id: string, progreso: Progreso): EstadoLeccion` (`"pendiente"` si no hay registro).
    - `indicePistas(pistas: Array<0 | 1 | 2 | "solucion">): number | null` (promedio con `"solucion"` = 3; `null` si la lista está vacía).
    - `ordenarLecciones<T extends { fase: number; orden: number }>(xs: T[]): T[]`
    - `registrosHuerfanos(progreso: Progreso, idsLecciones: string[]): string[]`
  - `src/logica/repasos.ts`:
    - `type Repaso = { id: string; fecha: string; tipo: "7 días" | "30 días"; estado: "proximo" | "toca" | "pasado" }`
    - `calcularRepasos(progreso: Progreso, hoy: string): Repaso[]`. Solo lecciones `dominada` con `fin`. Fechas `fin + 7` y `fin + 30`. Estado: `toca` si `hoy − 6 ≤ fecha ≤ hoy`, `proximo` si `fecha > hoy` y `pasado` si `fecha < hoy − 6`. Ordenado por fecha ascendente. Aritmética de fechas en UTC sobre texto `YYYY-MM-DD`.
  - `src/logica/rutas.ts`: `rutaLeccion(id: string, base: string): string` → `<base con una sola "/" final>lecciones/<id en minúsculas>/`.

- [ ] **Step 1 [Tú]: Crea el proyecto con versiones exactas**

```bash
mkdir sitio && cd sitio
echo "save-exact=true" > .npmrc && echo "24" > .node-version
pnpm init
pnpm add astro@7.3.8 @astrojs/starlight@0.42.6 yaml@2.9.1 @fontsource/inter@5.3.0
pnpm add -D vitest@5.0.4 typescript@6.0.3 @astrojs/check@0.9.10
```

En `package.json`: `"type": "module"`, `"packageManager": "pnpm@12.11.2"`, `"engines": {"node": ">=22.12.0"}` y los scripts `dev: astro dev`, `build: astro build`, `preview: astro preview`, `check: astro check` y `test: vitest run`.

- [ ] **Step 2 [Tú]: Configura Astro y Starlight**
  - `astro.config.ts`: `site: 'https://<USUARIO>.github.io'`, `base: '/roadmap-ai-engineering'` e integración `starlight({ title: 'Roadmap AI Engineering', defaultLocale: 'root', locales: { root: { label: 'Español', lang: 'es' } } })`.
  - `src/content.config.ts`: según la guía oficial de Starlight (`docsLoader()` y `docsSchema()`), con `docsSchema({ extend: z.object({ leccion: leccionSchema.optional() }) })`.
  - `src/content/docs/index.mdx`: título y dos enlaces relativos: `[Avance](avance/)` y `[Repasos](repasos/)`.

Run: `pnpm build`
Expected: build exitoso, con `dist/index.html`.

- [ ] **Step 3 [Claude Code]: Escribe las pruebas (fallan)**

```ts
// tests/contratos.test.ts — tabla [contrato, definicion, esquema]:
// [leccion.v1, leccion, leccionSchema], [leccion.v1, catalogo, catalogoSchema],
// [leccion.v1, fases, fasesSchema], [progreso.v1, raiz, progresoSchema].
// Cada YAML de validos/ -> safeParse(...).success === true; cada uno de invalidos/ -> false.
// Ruta literal: new URL('../../contratos/ejemplos/', import.meta.url)

// tests/progreso.test.ts
expect(estadoDe('L05', { lecciones: {} })).toBe('pendiente')
expect(indicePistas([0, 1, 2, 'solucion'])).toBe(1.5)
expect(indicePistas([])).toBeNull()
expect(ordenarLecciones([{fase:1,orden:4},{fase:1,orden:3.5},{fase:1,orden:3}]).map(x => x.orden)).toEqual([3, 3.5, 4])
expect(registrosHuerfanos({ lecciones: { L00: {estado:'en_curso'}, L99: {estado:'en_curso'} } }, ['L00'])).toEqual(['L99'])

// tests/repasos.test.ts — L00 dominada con fin 2026-10-01
expect(calcularRepasos(p, '2026-10-08')).toEqual([
  { id: 'L00', fecha: '2026-10-08', tipo: '7 días', estado: 'toca' },
  { id: 'L00', fecha: '2026-10-31', tipo: '30 días', estado: 'proximo' },
])
expect(calcularRepasos(p, '2026-10-20')[0].estado).toBe('pasado')
// fin 2026-01-25 -> '2026-02-01' y '2026-02-24'; una lección en_curso no genera repasos

// tests/rutas.test.ts
expect(rutaLeccion('L00', '/roadmap-ai-engineering')).toBe('/roadmap-ai-engineering/lecciones/l00/')
expect(rutaLeccion('L00', '/roadmap-ai-engineering/')).toBe('/roadmap-ai-engineering/lecciones/l00/')
expect(rutaLeccion('L00', '/')).toBe('/lecciones/l00/')

// tests/cargar.test.ts — con YAML de tests/datos/
// progreso válido -> objeto; progreso con campo desconocido -> rejects.toThrow(/progreso-mal\.yaml/)
```

- [ ] **Step 4 [Tú]: Verifica que fallan.** Run: `pnpm test`. Expected: FAIL.

- [ ] **Step 5 [Claude Code]: Implementa** `src/esquemas/*`, `src/datos/*` y `src/logica/*` con las interfaces de arriba.

- [ ] **Step 6 [Tú]: Verifica.** Run: `pnpm test && pnpm check && pnpm build`. Expected: pruebas en verde, `0 errors` en `astro check` y build exitoso.

- [ ] **Step 7 [Tú]: Escribe `departamento.yaml`** (`nombre: sitio`, `publica: []`, `consume: [leccion.v1, progreso.v1, estilo.v1]`) y `CLAUDE.md`. Este último explica que las rutas a otros departamentos viven solo en `src/datos/rutas.ts` y que el sitio no escribe en carpetas de otros departamentos.

Run (desde la raíz): `uv run --project herramientas guarda-independencia`
Expected: sin errores.

- [ ] **Step 8 [Tú]: Escribe `.github/workflows/sitio.yml`.** `paths: [sitio/**, contratos/**, lecciones/**, bitacora/**, .github/workflows/sitio.yml]`. Instala pnpm (`pnpm/action-setup`) y Node (`actions/setup-node` con `node-version-file: sitio/.node-version`). En `sitio/` corre `pnpm install --frozen-lockfile`, `pnpm test`, `pnpm check` y `pnpm build`.

- [ ] **Step 9 [Tú]: Abre el PR** (rama `sitio/base`).

---

### Task 7: Sitio — adaptador de lecciones y componentes MDX

**Files:**
- Create: `sitio/src/adaptador/{transformar,integracion}.ts`
- Create: `sitio/src/componentes/{Cita,ListaFuentes,Paso,Pista,Solucion,Comprobacion,Diagrama}.astro`
- Modify: `sitio/astro.config.ts` (registrar la integración)
- Test: `sitio/tests/transformar.test.ts`, `sitio/tests/datos/contenido/L99-prueba.mdx`, `sitio/tests/datos/catalogo-prueba.yaml`
- Modify: `.github/workflows/sitio.yml` (build de prueba)

**Interfaces:**
- Consumes: `leccionSchema`, `Catalogo`, `RUTA_CONTENIDO`, `RUTA_CATALOGO` y `cargarCatalogo` (Tarea 6).
- Produces:
  - `type FuenteResuelta = { n: number; id: string; titulo: string; url: string; tipo: FuenteCatalogo['tipo']; verificado: string; autores?: string[]; edicion?: string; isbn?: string; capitulo?: string; paginas?: string }`
  - `transformarLeccion(fuenteMdx: string, catalogo: Catalogo, origen: string): { nombreArchivo: string; contenido: string }`. Lanza `Error` con mensaje que empieza con `origen` si la cabecera no cumple `leccionSchema`. Salida:
    - `nombreArchivo`: `<id en minúsculas>.mdx`.
    - Cabecera: `title: <titulo>`, `sidebar: { order: fase * 100 + orden, label: '<id> · <titulo>' }` y `leccion: <cabecera original>`.
    - Después de la cabecera, un bloque de imports desde `'../../../componentes/<Nombre>.astro'` para los 7 componentes.
    - Fuera de bloques de código, cada `<Cita id="x" />` pasa a `<Cita id="x" n={k} />`, donde `k` es la posición de `x` (desde 1) en `fuentes`.
    - Al final: `## Fuentes` y `<ListaFuentes fuentes={[…FuenteResuelta en JSON]} />`.
  - `adaptadorLecciones(): AstroIntegration`, con `name: 'adaptador-lecciones'`. En el hook `astro:config:setup`:
    - Vacía `src/content/docs/lecciones/` y escribe ahí cada lección transformada.
    - Copia `contenido/diagramas/**` a `public/lecciones/diagramas/`.
    - Acepta las variables `ROADMAP_CONTENIDO` y `ROADMAP_CATALOGO` (rutas relativas a `sitio/`) para reemplazar las rutas por defecto. Solo las usa el build de prueba.
  - Componentes:
    - `Cita {id: string; n: number}` → `<sup><a href="#fuente-{n}">[{n}]</a></sup>`.
    - `ListaFuentes {fuentes: FuenteResuelta[]}` → lista ordenada con `id="fuente-{n}"`, tipo, capítulo y fecha de verificación.
    - `Paso {n: number; titulo: string}`.
    - `Pista {nivel: 1 | 2}` → `<details>` con resumen "Pista {nivel}".
    - `Solucion` → `<details>` con resumen "Solución".
    - `Comprobacion {comando: string; salida: string}` → dos bloques de código rotulados "Comando" y "Salida esperada".
    - `Diagrama {src: string; alt: string; pie?: string}` → `<figure>` con `src` prefijado por `import.meta.env.BASE_URL + 'lecciones/'`.

- [ ] **Step 1 [Claude Code]: Escribe `tests/transformar.test.ts` (falla)**, con una lección mínima válida (`id: L00`, `fase: 1`, `orden: 1`, `fuentes: [a, b]`):
  - `nombreArchivo` es `'l00.mdx'`.
  - La cabecera de salida, parseada con `yaml`, tiene `title`, `leccion.id === 'L00'` y `sidebar.order === 101`.
  - El contenido incluye una sola vez `import Cita from '../../../componentes/Cita.astro';`.
  - `<Cita id="b" />` en prosa → `<Cita id="b" n={2} />`.
  - `<Cita id="b" />` dentro de un bloque de código queda intacto.
  - El JSON de `ListaFuentes` contiene los títulos de `a` y `b` y el `capitulo` citado.
  - Una cabecera sin `objetivos` lanza un error que contiene el `origen`.

- [ ] **Step 2 [Tú]: Verifica que falla** (`pnpm test`).

- [ ] **Step 3 [Claude Code]: Implementa** `transformar.ts`, `integracion.ts` y los 7 componentes. Registra `adaptadorLecciones()` en `integrations` **antes** de `starlight(...)`.

- [ ] **Step 4 [Tú]: Verifica las pruebas unitarias** (`pnpm test && pnpm check`).

- [ ] **Step 5 [Tú]: Escribe la lección de prueba** `tests/datos/contenido/L99-prueba.mdx`. Debe usar los 7 componentes y tener un bloque con `ssh root@<IP_SERVIDOR>`; su catálogo va en `tests/datos/catalogo-prueba.yaml`.

Run: `ROADMAP_CONTENIDO=tests/datos/contenido ROADMAP_CATALOGO=tests/datos/catalogo-prueba.yaml pnpm build && grep -c 'id="fuente-1"' dist/lecciones/l99/index.html`
Expected: build exitoso y `1`.

- [ ] **Step 6 [Tú]: Agrega ese build de prueba como paso de `sitio.yml`**, antes del `pnpm build` normal.

- [ ] **Step 7 [Tú]: Abre el PR** (rama `sitio/adaptador`).

---

### Task 8: Sitio — avance, repasos, estilos y publicación

**Files:**
- Create: `sitio/src/adaptador/tokens.ts`, `sitio/src/componentes/{MapaRoadmap,GraficaPistas}.astro`, `sitio/src/pages/{avance,repasos}.astro`, `sitio/src/estilos/{sitio,impresion}.css`
- Modify: `sitio/src/adaptador/integracion.ts` (generar `src/estilos/tokens.css`), `sitio/astro.config.ts`
- Test: `sitio/tests/tokens.test.ts`
- Create: `.github/workflows/pages.yml`

**Interfaces:**
- Consumes: `cargarFases`, `cargarProgreso`, `estadoDe`, `indicePistas`, `ordenarLecciones`, `registrosHuerfanos`, `calcularRepasos`, `rutaLeccion` y `RUTA_TOKENS` (Tareas 6 y 7). La lista de lecciones se obtiene con `getCollection('docs')`, filtrando las entradas con `data.leccion`.
- Produces:
  - `type TokensEstilo = { color: { fondo: string; negro: string; rojo: string }; tipografia: { familia: string; pesos: number[] }; medida: { regla_px: number } }`
  - `tokensCss(tokens: TokensEstilo): string` → bloque `:root` con `--rm-color-fondo`, `--rm-color-negro`, `--rm-color-rojo`, `--rm-fuente` y `--rm-regla`.
  - Páginas `/avance/` y `/repasos/`, ambas con el componente `StarlightPage` de Starlight.

- [ ] **Step 1 [Claude Code]: Escribe `tests/tokens.test.ts` (falla).** Con el archivo real de tokens, la salida contiene `--rm-color-fondo: #f1efe9;`, `--rm-color-negro: #111111;`, `--rm-color-rojo: #e3120b;`, `--rm-fuente: "Inter"` y `--rm-regla: 6px;`.

- [ ] **Step 2 [Tú]: Verifica que falla; [Claude Code] implementa `tokensCss`** y su escritura en `integracion.ts`; **[Tú] verifica que pasa** (`pnpm test`).

- [ ] **Step 3 [Claude Code]: Componentes y páginas**
  - `MapaRoadmap {fases; lecciones; progreso; base}`: una columna por fase con su prefijo, título e hito. Cada lección es un enlace `rutaLeccion(id, base)` coloreado según `estadoDe`.
  - `GraficaPistas {lecciones; progreso}`: barras SVG en línea con `indicePistas` por lección, agrupadas por fase, sin librerías.
  - `avance.astro`: muestra los dos componentes. Si `registrosHuerfanos` no está vacío, imprime una advertencia en la consola del build y no falla.
  - `repasos.astro`: incrusta el progreso como JSON en `<script type="application/json" id="datos-progreso">`. Un `<script>` cliente calcula `hoy` con `new Date().toLocaleDateString('en-CA', { timeZone: 'America/Mexico_City' })`, llama a `calcularRepasos` y dibuja una tabla con los estados `toca`, `proximo` y `pasado`.

- [ ] **Step 4 [Tú]: Estilos**
  - En `astro.config.ts`, `customCss: ['@fontsource/inter/400.css', '@fontsource/inter/500.css', '@fontsource/inter/800.css', '@fontsource/inter/900.css', './src/estilos/tokens.css', './src/estilos/sitio.css', './src/estilos/impresion.css']`.
  - Agrega al `sidebar` los enlaces a Avance y Repasos, y el grupo "Lecciones" con `autogenerate: { directory: 'lecciones' }`.
  - En `sitio.css`, conecta los tokens con Starlight: `--sl-color-accent: var(--rm-color-rojo)` y `--sl-font: var(--rm-fuente), system-ui, sans-serif`.
  - `impresion.css`, dentro de `@media print`: oculta encabezado, barras laterales y buscador (usa los selectores que muestre el inspector del navegador en la versión instalada) y evita cortar figuras entre páginas.

- [ ] **Step 5 [Tú]: Verifica en el navegador**

Run: `ROADMAP_CONTENIDO=tests/datos/contenido ROADMAP_CATALOGO=tests/datos/catalogo-prueba.yaml pnpm build && pnpm preview`
Expected:
- `/roadmap-ai-engineering/avance/` muestra las 6 fases y el enlace de L99 lleva a su página.
- `/roadmap-ai-engineering/repasos/` carga sin errores en consola.
- La vista de impresión de la lección L99 muestra solo el contenido.

- [ ] **Step 6 [Tú]: Revisión de enlaces internos (spec §6.3).** Agrega a `sitio.yml`, después del build, `lycheeverse/lychee-action` en modo `--offline` sobre `sitio/dist/**/*.html`, mapeando la base `/roadmap-ai-engineering/` a `sitio/dist/` (con la opción `--remap` o `--root-dir` que ofrezca la versión instalada).

Run: agrega temporalmente `[roto](/roadmap-ai-engineering/no-existe/)` a `src/content/docs/index.mdx`, corre la misma revisión en local y luego quita el enlace.
Expected: la revisión falla con el enlace roto y pasa sin él.

- [ ] **Step 7 [Tú]: Escribe `.github/workflows/pages.yml`** según la guía oficial de Astro:
  - Se dispara en `push` a `main`, con los mismos `paths` que `sitio.yml`, y con `workflow_dispatch`.
  - Permisos: `contents: read`, `pages: write`, `id-token: write`.
  - Job `build`: `actions/checkout@v7` y `withastro/action@v6` con `path: ./sitio`.
  - Job `deploy`: `actions/deploy-pages@v5` con `environment: github-pages`.
  - En GitHub: Settings → Pages → Source: **GitHub Actions**.

- [ ] **Step 8 [Tú]: Abre el PR** (rama `sitio/avance`). Después del merge:

Run: `gh run watch` y luego `curl -sI https://<USUARIO>.github.io/roadmap-ai-engineering/ | head -n 1`
Expected: `HTTP/2 200`.

---

### Task 9: pre-commit, Dependabot y reglas de `main` (raíz)

**Files:**
- Create: `.pre-commit-config.yaml`, `.github/dependabot.yml`
- Modify: `README.md` (sección "Cómo trabajar")

**Interfaces:**
- Consumes: los CLIs de las Tareas 2 a 5 y los scripts del sitio.

- [ ] **Step 1 [Tú]: Escribe `.pre-commit-config.yaml`**
  - Hooks locales con `language: system`:
    - `guarda-binarios` y `guarda-independencia` (`uv run --project herramientas …`).
    - `validar-contratos` (con `files: ^contratos/`).
    - `validar-lecciones` (con `files: ^(lecciones|contratos)/`).
    - `validar-progreso` (con `files: ^(bitacora|contratos)/`).
  - El hook `gitleaks` del repositorio oficial de gitleaks.

- [ ] **Step 2 [Tú]: Instálalo y fija las versiones**

```bash
uv tool install pre-commit==4.7.0
pre-commit install
pre-commit autoupdate
pre-commit run --all-files
```

Expected: todos los hooks `Passed`.

- [ ] **Step 3 [Tú]: Escribe `.github/dependabot.yml`**, con revisión semanal (`interval: weekly`) para:
  - `npm` en `/sitio`.
  - `uv` en `/herramientas`, `/contratos`, `/lecciones` y `/bitacora`.
  - `github-actions` en `/`.

- [ ] **Step 4 [Tú]: Abre el PR** (rama `raiz/automatizacion`). Después del merge, crea la regla de `main`: Settings → Rules → Rulesets → New branch ruleset.
  - Objetivo `main`: exigir PR, exigir el check **`guardas`** y bloquear force push.
  - Exige solo `guardas`: los demás workflows tienen filtros de rutas y, si los marcas como requeridos, se quedan "pendientes" para siempre en PR que no los disparan.

Run: `git commit --allow-empty -m "prueba" && git push origin main`
Expected: el push es rechazado por la regla. Después ejecuta `git reset --hard origin/main`.

---

### Task 10: Lección L00 (departamento `lecciones/`)

**Files:**
- Create: `lecciones/contenido/L00-roadmap-como-codigo.mdx`
- Create (opcional): `lecciones/contenido/diagramas/l00-departamentos.svg`
- Modify: `lecciones/fuentes/catalogo.yaml`

**Interfaces:**
- Consumes: el contrato `leccion.v1` y el validador (Tarea 4). El sitio la muestra sin cambios en su código (Tareas 7 y 8).

- [ ] **Step 1 [Tú]: Agrega al catálogo las fuentes de L00**, verificando cada una:
  - `pro-git-2e` (ya existe; citarás capítulos).
  - `github-actions-docs` y `github-pages-docs` (oficial, docs.github.com).
  - `astro-deploy-github` (oficial, https://docs.astro.build/en/guides/deploy/github/).
  - `starlight` (oficial, https://starlight.astro.build/).
  - `json-schema-2020-12` (estandar, https://json-schema.org/draft/2020-12).
  - `pre-commit` (oficial, https://pre-commit.com/).
  - `claude-code-memory` (oficial, https://code.claude.com/docs/en/memory).

- [ ] **Step 2 [Tú]: Escribe la cabecera**
  - Datos: `id: L00`, `titulo: El roadmap como código`, `fase: 1`, `orden: 1`, `prerequisitos: []`.
  - `objetivos` (de 2 a 4, verificables). Por ejemplo: "Creas un repo y trabajas solo con ramas y PRs", "Escribes un workflow de GitHub Actions que valida contenido", "Publicas un sitio en GitHub Pages desde CI", "Explicas qué es un contrato de datos y qué protege".
  - `laboratorio.verificacion.comando: curl -sI https://<USUARIO>.github.io/roadmap-ai-engineering/ | head -n 1`, `salida_esperada: HTTP/2 200` y `entorno` con tu sistema y versiones reales.
  - El bloque `reel` (tema, analogía, gancho, idea, ejemplo y cierre con sus `ancla`) lo escribes tú: es el guion de tu primer reel.

- [ ] **Step 3 [Tú, con ayuda de Claude Code para redactar]: Escribe el cuerpo** en el orden de la spec §2.2.
  - La escena: "quiero aprender en serio y documentarlo".
  - La intuición, con su diagrama de departamentos.
  - Cómo funciona de verdad, con `<Cita>`.
  - El laboratorio guiado: los pasos que hiciste en las Tareas 1 a 9, con `<Paso>`, `<Pista>`, `<Solucion>` y `<Comprobacion>`. Las salidas se copian de tu terminal.
  - Errores comunes (los que te pasaron).
  - Las 3 preguntas de recuerdo y el reto de 60 segundos.

- [ ] **Step 4 [Tú]: Valida y revisa en local**

Run: `cd lecciones && uv run validar-lecciones && cd ../sitio && pnpm build && pnpm preview`
Expected: `0 errores` y la página `/roadmap-ai-engineering/lecciones/l00/` con sus citas numeradas y la lista de fuentes.

- [ ] **Step 5 [Tú]: Revisión independiente.** En una sesión nueva de Claude Code que no haya redactado la lección, pide: "Compara cada afirmación de `contenido/L00-roadmap-como-codigo.mdx` con la fuente citada y lista las que no estén respaldadas". Corrige lo que salga.

- [ ] **Step 6 [Tú]: Abre el PR** (rama `lecciones/l00`). Tras el merge, `pages.yml` publica la lección.

---

### Task 11: Registrar L00 y cerrar el laboratorio (departamento `bitacora/`)

**Files:**
- Modify: `bitacora/progreso.yaml`
- Create: `bitacora/evidencias/l00-sitio.png`

**Interfaces:**
- Consumes: el contrato `progreso.v1`; el sitio lo refleja en `/avance/` y `/repasos/`.

- [ ] **Step 1 [Tú]: Marca el laboratorio como verificado.** Guarda una captura del sitio publicado en `evidencias/l00-sitio.png`. Actualiza L00: `estado: lab_verificado`, `horas`, `pistas` (de tu libreta, un valor por paso [Tú]) y `evidencia: {commit: <sha del merge de la Tarea 10>, captura: evidencias/l00-sitio.png}`.

Run: `uv run validar-progreso`
Expected: `0 errores`.

- [ ] **Step 2 [Tú]: Comprueba que la dominas.** Responde sin mirar las 3 preguntas de recuerdo de L00 y explica el tema en voz alta en 60 segundos. Si aciertas las 3, actualiza: `estado: dominada`, `fin: <hoy>`, `recuerdo: {fecha: <hoy>, aciertos: 3}` y `explicacion_60s: true`.

Run: `uv run validar-progreso`
Expected: `0 errores`.

- [ ] **Step 3 [Tú]: Abre el PR** (rama `bitacora/l00`). Tras el merge, verifica en el sitio publicado que L00 aparece como dominada en `/avance/` y que `/repasos/` muestra sus fechas de 7 y 30 días.
