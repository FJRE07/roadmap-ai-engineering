# CLAUDE.md — raíz de roadmap-ai-engineering

## Departamentos (spec §1.2)

| Departamento | Publica (su superficie pública) | Consume (solo vía contrato) |
|---|---|---|
| `lecciones/` | Archivos MDX de lecciones, `fuentes/catalogo.yaml` y `fases.yaml` (`leccion.v1`); `salida/guiones/*.json` (`guion.v1`, desde SP2) | Nada |
| `bitacora/` | `progreso.yaml` (`progreso.v1`) | Nada |
| `reels/` | `salida/publicados.json` (`reel-publicado.v1`: por lección, el número congelado del reel, la URL del video y una lista de `destinos` con red, URL y fecha) y los MP4 como assets de GitHub Releases | `guion.v1`, `estilo.v1` |
| `sitio/` | El sitio web construido | `leccion.v1`, `progreso.v1`, `reel-publicado.v1`, `estilo.v1` |
| `servicio/` | Imagen Docker con tag y su API documentada (OpenAPI) | Nada |
| `infra/` | Entornos desplegados e `inventario.yaml` (nodos, discos, red; §3.3) | Las imágenes y builds publicados, mediante un contrato `despliegue.v1` que nace la primera vez que infra despliega algo de otro departamento |

## Reglas de independencia (spec §1.3)

1. **Sin código compartido.** Ningún departamento importa ni referencia archivos internos de otro; solo lee rutas declaradas como públicas.
2. **Herramientas propias.** Cada departamento tiene sus dependencias y su archivo de bloqueo (pnpm por departamento, sin workspace compartido; uv para `servicio/`), su `README.md`, su `CLAUDE.md` y su propia versión con tags (`reels-v0.3.0`). Actualizar una librería de los reels no toca nada del sitio.
3. **Los contratos cambian por versión, nunca en sitio.** Un cambio incompatible crea `v2` junto a `v1`. Cada consumidor migra cuando quiere, y `v1` se retira cuando nadie lo usa. Los cambios compatibles (un campo opcional nuevo) se permiten dentro de la misma versión.
4. **Un PR, un departamento.** Un PR toca solo archivos de un departamento. Un cambio a `contratos/` va en su propio PR y dispara las pruebas de contrato de todos los departamentos que lo consumen.
5. **El estilo se comparte como datos, no como componentes.** `estilo.v1.tokens.json` define colores, tipografías y medidas. Reels y sitio implementan sus componentes por separado y cada uno empaqueta sus fuentes tipográficas (licencia OFL).

## Cómo trabajar aquí

Abre Claude Code dentro de la carpeta del departamento en que trabajas; no edites fuera de ella. Si necesitas cambiar un contrato, detente y propón un PR solo de `contratos/`.

## Regla de aprendizaje

En los pasos del plan marcados **[Tú]**, da solo la pista pedida (**nivel 1** o **nivel 2**). La solución completa, únicamente si se pide explícitamente.

## Fuentes y archivos prohibidos

- **Claude no es fuente** (spec §5.4). Lo que Claude redacte entra solo si lo respalda una fuente citable; las salidas esperadas se copian de una ejecución real, nunca se inventan.
- **Nada de PDF, EPUB ni secretos en Git.**
