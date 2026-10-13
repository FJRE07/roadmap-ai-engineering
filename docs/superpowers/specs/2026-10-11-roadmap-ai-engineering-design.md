# Roadmap: de Homelab a AI Engineering, MLOps y Cloud — Diseño

- **Fecha:** 2026-10-11 (revisión 2: departamentos independientes y catálogo de libros; revisión 3, 2026-10-12: compras del homelab, homelab y aprendizaje desacoplados, reglas de crecimiento)
- **Estado:** diseño aprobado por secciones en conversación; spec escrita en revisión
- **Autor:** Jair Rangel (diseño asistido por Claude)
- **Fuentes verificadas:** entre 2026-10-08 y 2026-10-11 (ver §10)

---

## 0. Entendimiento compartido

### Lo que se busca
Un roadmap profesional, muy visual e interactivo, para pasar de homelab a **AI Engineering, MLOps y Cloud**. Cada tema produce tres piezas:

1. **Lección:** teoría escrita y visual, con narrativa (storytelling) técnica y limpia, y fuentes citadas.
2. **Laboratorio:** práctica real que agrega, en orden, una pieza a un servicio vendible o enseñable.
3. **Reel:** el mismo tema explicado con analogías sencillas, animado con código (Remotion) y con tu voz grabada.

**Narrativa:** tú, un data scientist, extendiendo tus conocimientos hacia AI Engineering, MLOps y Cloud. Los laboratorios construyen un servicio de **inteligencia de contenido para creadores de Shorts/Reels** (Instagram primero, TikTok después). Todo se documenta como serie de "building in public", porque también grabas contenido.

### Lo que dijiste (requisitos)
- **Objetivos:** conseguir trabajo como AI Engineer, vender o enseñar, crecer en tu trabajo actual y dominar los temas a fondo.
- **Punto de partida:** "Tengo conocimiento, pero no profundo. Me guío mucho de Claude y quiero dejar de hacerlo tan directo. Saber cómo son los comandos."
- **Tiempo:** 15 horas o más por semana.
- **Presupuesto en herramientas:** $0. Sin After Effects ni suscripciones de Adobe.
- **Fuentes:** "Las fuentes que uses para cada cosa deberán ser confiables y que las podamos citar." Se quieren libros de referencia (O'Reilly y similares), que irás comprando.
- **Formato:** documento y página visual.
- **Estilo visual:** base Swiss con diagramas en tratamiento Newspaper; los diagramas se dibujan con p5.brush (decisión A tras el spike).
- **Reels:** generados por código, tu voz, analogías sencillas.
- **Departamentos independientes:** "si queremos modificar la parte de creación de reels no impacte en los demás, esto para todos los departamentos" (§1).
- **Ejecución:** la implementación la llevas tú con Claude Code, de la mano (§9).

### Hardware disponible
| Equipo | Rol en el roadmap |
|---|---|
| Lenovo ThinkCentre M75q Gen 5 (Ryzen 7 PRO 8700GE, 32 GB DDR5, SSD 512 GB). Según la ficha oficial: dos ranuras M.2 2280 PCIe 4.0 para SSD (Lenovo valida hasta 1 TB cada una), dos ranuras SODIMM DDR5 (32 GB máximo estándar; 64 GB solo por pedido especial) y Ethernet Gigabit con Wake-on-LAN [F-psref] | Servidor 24/7 con Proxmox: servicios, bases de datos, orquestación y sitio (más adelante) |
| Torre con RTX 4060 Ti 8 GB y fuente de 700 W | GPU bajo demanda, encendida por Wake-on-LAN: Ollama, whisper.cpp y renders |
| RTX 3050 (repuesto) | Sin rol asignado; no se depende de ella |
| Disco duro externo de 1 TB en gabinete USB-C | Destino de respaldos de Proxmox (L04) |
| Laptop i5 7.ª gen, 16 GB | Cliente y equipo de trabajo opcional |

### Supuestos (no dichos explícitamente; corregibles)
- La nube por defecto es **AWS**. Se confirma antes de la Fase 5.
- Las semanas por fase son estimaciones a unas 15 horas por semana.
- La página de avance es **pública** (parte del "building in public").

### Criterios de éxito
1. Cada fase cierra con su hito funcionando de verdad (§3).
2. El medidor de independencia (`pistas`, §5) baja de una fase a otra.
3. Beta del servicio con 3 a 5 creadores al terminar la Fase 5.
4. Portafolio y caso de estudio publicados al terminar la Fase 6.
5. Ninguna lección se publica sin pasar las verificaciones de citas (§5, §6).
6. Un cambio dentro de un departamento nunca rompe la CI de otro (§1, §6).

---

## 1. Arquitectura: departamentos independientes unidos por contratos

### 1.1 Principio
Monorepo en GitHub dividido en **departamentos**. Un departamento **nunca importa código de otro**: solo lee archivos publicados por otro departamento que cumplen un **contrato versionado**. Lo único compartido es la carpeta `contratos/`. Cambiar el interior de un departamento (por ejemplo, rehacer el kit visual de los reels) no puede afectar a los demás mientras siga cumpliendo sus contratos.

```
roadmap-ai-engineering/
├─ contratos/          Lo único compartido: esquemas JSON versionados
│  ├─ leccion.v1.schema.json
│  ├─ progreso.v1.schema.json
│  ├─ estilo.v1.tokens.json        colores, tipografías y medidas
│  ├─ guion.v1.schema.json         (nace en SP2)
│  ├─ reel-publicado.v1.schema.json (nace en SP2)
│  └─ ejemplos/        casos válidos e inválidos de cada contrato
├─ lecciones/          Depto. Contenido
├─ sitio/              Depto. Sitio (Astro + Starlight)
├─ reels/              Depto. Reels (Remotion, con su propio kit visual)
├─ servicio/           Depto. Servicio (Python)
├─ infra/              Depto. Infra (Proxmox, Docker y después Terraform)
├─ bitacora/           Depto. Bitácora: progreso.yaml (tu avance)
├─ herramientas/       Guardas del repo y utilidades (no las importa ningún depto.)
├─ biblioteca/         PDFs comprados; fuera de Git (.gitignore)
├─ CLAUDE.md           Mapa de departamentos y reglas de independencia
└─ .github/workflows/  Un workflow por departamento, más las guardas
```

### 1.2 Qué produce y qué consume cada departamento
| Departamento | Publica (su superficie pública) | Consume (solo vía contrato) |
|---|---|---|
| `lecciones/` | Archivos MDX de lecciones, `fuentes/catalogo.yaml` y `fases.yaml` (`leccion.v1`); `salida/guiones/*.json` (`guion.v1`, desde SP2) | Nada |
| `bitacora/` | `progreso.yaml` (`progreso.v1`) | Nada |
| `reels/` | `salida/publicados.json` (`reel-publicado.v1`: por lección, el número congelado del reel, la URL del video y una lista de `destinos` con red, URL y fecha) y los MP4 como assets de GitHub Releases | `guion.v1`, `estilo.v1` |
| `sitio/` | El sitio web construido | `leccion.v1`, `progreso.v1`, `reel-publicado.v1`, `estilo.v1` |
| `servicio/` | Imagen Docker con tag y su API documentada (OpenAPI) | Nada |
| `infra/` | Entornos desplegados e `inventario.yaml` (nodos, discos, red; §3.3) | Las imágenes y builds publicados, mediante un contrato `despliegue.v1` que nace la primera vez que infra despliega algo de otro departamento |

Cada departamento declara su superficie pública y los contratos que consume en un archivo `departamento.yaml` en su raíz.

### 1.3 Reglas de independencia
1. **Sin código compartido.** Ningún departamento importa ni referencia archivos internos de otro; solo lee rutas declaradas como públicas.
2. **Herramientas propias.** Cada departamento tiene sus dependencias y su archivo de bloqueo (pnpm por departamento, sin workspace compartido; uv para `servicio/`), su `README.md`, su `CLAUDE.md` y su propia versión con tags (`reels-v0.3.0`). Actualizar una librería de los reels no toca nada del sitio.
3. **Los contratos cambian por versión, nunca en sitio.** Un cambio incompatible crea `v2` junto a `v1`. Cada consumidor migra cuando quiere, y `v1` se retira cuando nadie lo usa. Los cambios compatibles (un campo opcional nuevo) se permiten dentro de la misma versión.
4. **Un PR, un departamento.** Un PR toca solo archivos de un departamento. Un cambio a `contratos/` va en su propio PR y dispara las pruebas de contrato de todos los departamentos que lo consumen.
5. **El estilo se comparte como datos, no como componentes.** `estilo.v1.tokens.json` define colores, tipografías y medidas. Reels y sitio implementan sus componentes por separado y cada uno empaqueta sus fuentes tipográficas (licencia OFL).

**Consecuencia aceptada:** el sitio **inserta el video renderizado** de cada reel (leído de `reel-publicado.v1`) en lugar de incrustar el reproductor interactivo de Remotion, que obligaría al sitio a importar código de los reels. Se pierde la interactividad paramétrica del reproductor; se conserva ver el reel dentro de la lección.

### 1.4 Cómo se garantiza
- **Guarda de independencia** (`herramientas/`): falla si un archivo de un departamento referencia rutas de otro que no estén en su superficie pública declarada.
- **Guarda de alcance del PR:** falla si un PR toca más de un departamento, o `contratos/` junto con otra carpeta.
- **Pruebas de contrato:** cada productor valida lo que publica contra el contrato; cada consumidor valida que su lector acepta los ejemplos válidos y rechaza los inválidos de `contratos/ejemplos/`.
- **Claude Code:** el `CLAUDE.md` de la raíz explica los departamentos y las reglas; el de cada departamento dice su stack, sus comandos y "no edites fuera de esta carpeta; si necesitas cambiar un contrato, detente y propón un PR de contrato". Claude Code carga los `CLAUDE.md` de las carpetas superiores al iniciar y los de subcarpetas cuando trabaja en ellas, pero los trata como contexto, no como reglas que se impongan [F-cc-memory]. Por eso la garantía real son las guardas de CI. Abrir Claude Code dentro de la carpeta del departamento (`cd reels && claude`) carga el `CLAUDE.md` de la raíz y el del departamento.

### 1.5 Flujo del contenido
- Cada lección es **un solo archivo** MDX con cabecera validada por `lecciones/` (§2).
- `lecciones/` exporta el guion de cada reel a `salida/guiones/<id>.json` (`guion.v1`) con el número del reel y las fuentes ya resueltas. Los reels nunca leen MDX ni el catálogo de fuentes.
- `sitio/` lee las lecciones, el catálogo, `fases.yaml`, `progreso.yaml` y `publicados.json`, y produce la **página web** (mapa, lecciones, avance y video del reel) y el **documento** (PDF con la impresión del navegador y una hoja de estilos de impresión).
- El código de cada laboratorio vive en `servicio/` o `infra/`; la lección enlaza al commit o a la carpeta.

### 1.6 Por qué Astro + Starlight (frente a MkDocs Material o Zensical)
- Acepta componentes de React en MDX y trae búsqueda, modo oscuro y accesibilidad [F-starlight]; los diagramas animados del sitio viven en `sitio/`.
- Valida la cabecera de las lecciones con un esquema al construir, como segunda capa además del validador de `lecciones/`.
- Comparte lenguaje con Remotion (TypeScript), así que el costo de aprender TypeScript se paga una sola vez, aunque cada departamento tenga sus propias dependencias.
- Material for MkDocs entró en modo mantenimiento en noviembre de 2025 [F-mkdocs]. Zensical, su sucesor, todavía no tenía todas las funciones en su anuncio.
- **Riesgo anotado:** Cloudflare compró Astro en 2026; anunció que seguirá siendo de código abierto [F-astro-cf]. Si hiciera falta cambiar de generador, solo se rehace `sitio/`: las lecciones no dependen de Astro.

**Dónde se publica:** primero en GitHub Pages, gratis. Después, como laboratorio, en tu homelab con Docker y un túnel de Cloudflare; GitHub Pages queda como respaldo si el homelab se cae.

### 1.7 Cómo crece sin romperse
| Lo que se agrega | Cómo entra | Qué no cambia |
|---|---|---|
| Una lección nueva | Recibe el siguiente id libre (L33, L34…); su `orden` dentro de la fase la coloca donde va, y puede ser decimal (3.5) para insertarla entre dos. | Los ids nunca se renumeran y el número de un reel se congela al publicarse, así que los reels ya publicados no cambian. |
| Una fase nueva | Una entrada en `fases.yaml` con su prefijo. | Nada más. |
| Un libro o fuente | Una entrada en el catálogo (§5.5). | Las lecciones existentes. |
| Un departamento nuevo (por ejemplo, `curso/` para vender el curso) | Su carpeta, su `departamento.yaml`, su `CLAUDE.md` y su workflow. | Ningún otro departamento. |
| Hardware nuevo (otro nodo, un NAS, un disco) | Una entrada en `infra/inventario.yaml` (§3.3). | Las lecciones, que hablan de roles y no de equipos concretos. |
| Un servicio nuevo en el homelab | Su propia carpeta en `infra/servicios/<nombre>/` con su archivo de Compose. | Los demás servicios, que se levantan y bajan por separado. |
| Una red social nueva (TikTok, YouTube Shorts) | Un elemento más en `destinos` de `reel-publicado.v1`. | El contrato, que no necesita nueva versión. |

---

## 2. Anatomía de una lección (departamento `lecciones/`)

### 2.1 Catálogo de fuentes y cabecera
Las fuentes se definen **una sola vez** en `lecciones/fuentes/catalogo.yaml`; las lecciones las citan por id. Así un libro que citan 10 lecciones tiene su edición e ISBN en un solo lugar.

```ts
// Notación ilustrativa del contrato leccion.v1 (JSON Schema en contratos/).
FuenteCatalogo = {
  id: string                       // "huyen-aie"
  titulo: string
  url: url                         // página oficial de la edición o del documento
  tipo: "oficial" | "paper" | "libro" | "estandar" | "apoyo"
  verificado: date
  autores?: string[]
  edicion?: string                 // obligatorio si tipo = "libro"
  isbn?: string                    // obligatorio si tipo = "libro"
  archivo_local?: string           // nombre del PDF en biblioteca/ (solo referencia)
}

Leccion = {
  id: string                       // "L03"; estable, nunca se renumera
  titulo: string
  fase: number                     // debe existir en fases.yaml
  orden: number                    // orden dentro de la fase; admite decimales para insertar
  duracion: { lectura_min: number, laboratorio_h: number }
  prerequisitos: string[]          // ids de lecciones
  objetivos: string[]              // de 2 a 4, verificables
  fuentes: { id: string, capitulo?: string, paginas?: string }[]
  laboratorio: {
    objetivo: string
    entregable: "commit" | "servicio" | "captura"
    verificacion: {
      comando: string              // usa roles del inventario: <IP_SERVIDOR>, no una IP fija
      salida_esperada: string
      entorno: string              // hardware y versiones con que se capturó la salida
    }
  }
  reel: {
    tema: string                   // "Modelos de lenguaje"
    analogia: string
    gancho:  { texto: string, ancla: string }   // ancla = palabra clave hablada
    idea:    { texto: string, ancla: string }
    ejemplo: { texto: string, ancla: string }
    cierre:  { texto: string }                  // "Lección completa en …"
    fuentes: string[]              // ids; deben estar en `fuentes` de la lección
  }
}
```

**Reglas (las aplica el validador de `lecciones/`)**
- Cada `fuentes[].id` existe en el catálogo.
- Al menos una fuente de la lección, una vez resuelta, tiene `tipo` distinto de `apoyo`.
- En el catálogo, `libro` exige `edicion` e `isbn`. En la lección, citar un `libro` exige `capitulo`.
- `reel.fuentes` es un subconjunto de las fuentes de la lección.
- `objetivos` tiene de 2 a 4 elementos.
- El número del reel (por ejemplo `IA / 01`) **se calcula** a partir de `fase` y `orden`, con el prefijo de la fase definido en `fases.yaml` (al inicio: HL, DT, ML, IA, CL y PR). Al publicarse el reel, su número queda **congelado** en `publicados.json`.
- **Componentes MDX permitidos** (parte del contrato `leccion.v1`): `Cita`, `Paso`, `Pista`, `Solucion`, `Comprobacion` y `Diagrama`. El sitio debe implementarlos todos; una lección no puede usar otros.

`lecciones/fases.yaml` guarda por fase su número, prefijo, título, semanas estimadas, hito y lecturas base (ids del catálogo).

### 2.2 Cuerpo (siempre en este orden)
1. **La escena:** tu problema real en ese punto del proyecto ("mis cron solo corren si mi laptop está prendida").
2. **La intuición:** la analogía, con un diagrama.
3. **Cómo funciona de verdad:** explicación técnica con `<Cita id="…"/>` en cada afirmación importante.
4. **Laboratorio guiado:** en cada paso **tú escribes el comando**. Las ayudas están escalonadas y plegadas: pista 1, pista 2 y, al final, la solución. Cada paso termina con un comando de comprobación y su salida esperada.
5. **Errores comunes:** fallos típicos y cómo diagnosticarlos.
6. **Comprueba que lo dominas:** 3 preguntas de recuerdo sin mirar y el reto de explicarlo en voz alta en 60 segundos (el ensayo del reel).
7. **Fuentes:** lista generada desde la cabecera y el catálogo.

**Tamaño:** de 20 a 40 minutos de lectura y de 1 a 3 horas de laboratorio. Si una lección se pasa, se divide.

---

## 3. Fases y laboratorios

Cada fase cierra con un **hito del servicio** que funciona de verdad y con un **reel de episodio** sobre tu avance.

| Fase | Semanas | Hito | Lecciones |
|---|---|---|---|
| 1 · Homelab | ~4 | Tu servidor listo y tus cron corriendo solos | L00 El roadmap como código (repo, Astro, CI, GitHub Pages) · L01 Proxmox, primera VM y SSH con llaves · L02 Redes: IP fija, switch, VLAN y Tailscale · L03 Docker y Compose, y tus cron migrados desde GitHub · L04 Almacenamiento, snapshots y respaldos 3-2-1 · L05 Monitoreo básico y UPS |
| 2 · Datos del creador | ~4 | Tu propio dashboard de desempeño | L06 API de Instagram: OAuth, tokens, límites, privacidad y términos de uso · L07 Ingesta programada a Postgres · L08 Modelado y calidad de datos · L09 Orquestación (Prefect) · L10 Análisis de tus reels y dashboard |
| 3 · ML y MLOps | ~5 | Predictor de desempeño servido por API | L11 Variables de un reel (hora, duración, gancho) · L12 Modelo base con validación temporal · L13 Experimentos (MLflow) y versionado de datos (DVC) · L14 Servir el modelo (FastAPI, Docker, pruebas) · L15 Drift y reentrenamiento programado |
| 4 · LLMs y AI Engineering | ~6 | Copiloto de contenido | L16 Cómo funciona un LLM, y Ollama en tu torre con Wake-on-LAN · L17 Transcripción de tus videos · L18 Prompts y salidas estructuradas para analizar ganchos · L19 Embeddings y RAG sobre tus guiones (pgvector) · L20 Evaluación de LLMs · L21 Agente con herramientas para ideas y guiones · L22 Fine-tuning con LoRA (GPU rentada por horas) · L23 Gateway, observabilidad y costos |
| 5 · Cloud y producción | ~5 | Beta con 3 a 5 creadores | L24 Infraestructura como código (Terraform) · L25 Contenedores y base de datos gestionada · L26 CI/CD con staging y producción · L27 Seguridad, secretos y OAuth multiusuario · L28 Observabilidad y costos · L29 Arquitectura híbrida: homelab para desarrollo y GPU, nube para producción |
| 6 · Producto y profesión | ~3 | Producto vendible y caso de estudio | L30 Multiusuario, cobros y onboarding · L31 TikTok (publicación) · L32 Portafolio, caso de estudio y entrevistas de diseño de sistemas |

**Total:** ~27 semanas, unos 7 meses.

**Por qué este orden:** sin datos no hay modelo, sin modelo servido no hay MLOps y sin infraestructura reproducible no hay nube. El ML clásico (Fase 3) va antes que los LLMs: aprendes el ciclo de MLOps con un modelo barato y medible, y luego lo aplicas a los LLMs, donde evaluar es más difícil.

### 3.1 Lecturas base por fase
Los libros son la columna teórica; la documentación oficial manda en lo que cambia rápido (APIs y versiones). Cada lección cita **el capítulo exacto**. Esta tabla es el contenido inicial de `fases.yaml` y del catálogo; sumar libros después sigue §5.5.

| Fase | Lecturas |
|---|---|
| 1 | *How Linux Works*, 3.ª ed., Brian Ward (No Starch) · *Docker: Up & Running*, 3.ª ed., Kane y Matthias (O'Reilly) [F-docker] · *Pro Git*, Chacon y Straub (gratis en git-scm.com) |
| 2 | *Fundamentals of Data Engineering*, Reis y Housley (O'Reilly) · *Designing Data-Intensive Applications*, 2.ª ed., Kleppmann y Riccomini (O'Reilly, 2026) [F-ddia] |
| 3 | *Designing Machine Learning Systems*, Chip Huyen (O'Reilly) · *Hands-On Machine Learning with Scikit-Learn and PyTorch*, Géron (O'Reilly, 2025) [F-geron] |
| 4 | *AI Engineering*, Chip Huyen (O'Reilly, 2025) [F-aie] · *Hands-On Large Language Models*, Alammar y Grootendorst (O'Reilly, 2024) [F-hollm] · *Build a Large Language Model (From Scratch)*, Raschka (Manning) |
| 5 | *Terraform: Up & Running*, 3.ª ed., Brikman (O'Reilly) [F-terraform] · *Site Reliability Engineering*, Google (gratis en sre.google) |
| 6 | Se repasan *Designing Data-Intensive Applications* y *AI Engineering* para entrevistas de diseño de sistemas |

**Compra sugerida por etapas:** primero *AI Engineering*, *Designing Machine Learning Systems* y *DDIA 2.ª ed.*; el resto al llegar a cada fase. Gratuitos y legales: *Pro Git*, *Site Reliability Engineering* y *The Linux Command Line* (William Shotts).

**Acceso legal:** O'Reilly dejó de vender ebooks en su tienda en 2017; eBooks.com los vendía sin DRM [F-ebooks] (dato de 2017: confirmar "DRM-free" en cada libro). Otra opción es la membresía profesional de ACM con el Skills Bundle [F-acm]. No se usan ni se enlazan copias no autorizadas.

### 3.2 Compras del homelab: justo a tiempo
**Regla:** se compra una pieza cuando la próxima lección la necesita, no antes. Lo que no pide ninguna lección va a `bitacora/ideas.md` hasta que una medición lo justifique. Precios en MXN vistos el 7 de octubre de 2026 en tiendas mexicanas ("est." = estimación); se confirman antes de pagar.

| Prioridad | Compra | La necesita | Precio visto | Notas |
|---|---|---|---|---|
| 1 | USB de 8 a 16 GB | L01 (instalar Proxmox) | $100 a $200 (est.) | Solo para el instalador. |
| 1 | Switch de 8 puertos con VLANs (TP-Link TL-SG108E o Netgear GS308E) | L01 y L02 | **Pedido el 12-oct** (TL-SG108E; llega del 14 al 19-oct) | Tu cuarto tiene una sola salida de red: sin switch no conectas por cable la torre y el servidor a la vez. Las VLANs son parte de L02. Verifica la "E" en el modelo. |
| 1 | 3 cables Cat6 de cobre puro (salida de pared a switch, switch a torre, switch a servidor) | L01 | $40 a $150 c/u (est.) | Evita los "CCA". Mide cada tramo y suma medio metro. |
| 2 | Disco duro externo para respaldos | L04 (respaldos 3-2-1) | **Ya lo tienes** (HDD de 1 TB en gabinete USB-C) | Uno de 2 TB ($1,372 a $1,799) solo si los respaldos dejan de caber. |
| 3 | UPS de 1000 VA con **puerto USB de datos** | L05 (UPS y apagado ordenado con NUT) | **Pedido el 12-oct** (CyberPower UT1000GU, 1000 VA / 500 W, USB HID [F-cyberpower]; llega del 14 al 19-oct) | Confirma en la ficha que el USB sea de datos y no solo de carga; sin él no hay apagado automático. Conecta servidor y switch. |
| 4 | SSD NVMe M.2 2280 PCIe 4.0 de 1 TB, con garantía | Cuando el disco pase del 70 % (probablemente en la Fase 4: modelos, videos y embeddings) | $800 a $1,600 (precios viejos) | Va en la segunda ranura M.2. Lenovo valida hasta 1 TB por ranura [F-psref]. |
| 5 | Rack de 10" (Tecmojo 6U de pared, 25 cm de fondo), velcro y etiquetas | Ninguna lección | ~$1,534 el 6U (sin verificar la versión profunda) | Orden y buena imagen para grabar; no cambia lo que aprendes. El servidor mide 179 × 182.9 × 36.5 mm [F-psref]. |
| Solo con medición | RAM a 64 GB (2×32 GB DDR5 SODIMM) | Si Proxmox muestra memoria insuficiente | Sin cotizar | Lenovo solo la ofrece por pedido especial [F-psref]. |
| Solo con medición | KVM por IP, monitor de 10", adaptador USB a 2.5 GbE | Si una necesidad concreta lo pide | Sin cotizar | Opcionales. |
| Sin compra | RTX 3050 dentro de la torre, junto a la 4060 Ti | Si en la Fase 4 necesitas más de 8 GB de VRAM local | $0 | Requiere ranura PCIe libre, espacio y, si es la versión de 8 GB, un conector de 8 pines libre. L22 usa GPU rentada de todos modos. |

### 3.3 El homelab cambia; tu aprendizaje no se pierde
- **Tu avance no vive en el homelab.** `bitacora/progreso.yaml` está en Git y en GitHub. Reinstalar Proxmox, cambiar un disco o sumar un nodo no borra nada de tu avance.
- **Evidencia duradera.** La evidencia de un laboratorio es un commit o una captura guardada en `bitacora/evidencias/`. Una URL de un servicio corriendo se acepta solo junto con una de esas dos, porque deja de responder si el homelab cambia.
- **Las lecciones hablan de roles, no de equipos.** `infra/inventario.yaml` describe tus nodos con un rol (`servidor-24x7`, `gpu-bajo-demanda`), sus discos y tu red (IPs y VLANs). Los laboratorios usan `<IP_SERVIDOR>` o `<NODO_GPU>`, no valores fijos. Si cambias el hardware, cambia el inventario, no las lecciones.
- **Salidas con su entorno.** Cada salida esperada guarda el `entorno` en que se capturó. Si después de una mejora la salida cambia (otro nombre de disco, otra versión), se sabe por qué.
- **Primero a mano, después como código.** Lo que haces a mano en un laboratorio queda luego en `infra/` (scripts y archivos de Compose; desde L24, Terraform). Reinstalar o mejorar el homelab es volver a aplicar lo que está en Git, no rehacerlo de memoria.
- **Cada mejora es una mini lección.** Las mejoras de hardware se registran en `progreso.yaml` bajo `mejoras` (fecha, qué, por qué y evidencia) y pueden tener su reel. No bloquean la ruta principal.
- **Contra el "yak shaving":** las mejoras se hacen solo cuando una lección las pide o al cerrar el hito de una fase. Mientras, se anotan en `bitacora/ideas.md`.

---

## 4. Estilo visual y producción de reels (departamento `reels/`)

### 4.1 Estilo (fijado tras las muestras)
Los valores compartidos viven en `contratos/estilo.v1.tokens.json`; los componentes, dentro de cada departamento.

- **Base Swiss:** fondo `#f1efe9`, negro `#111111`, un solo acento rojo `#e3120b` e Inter. Retícula con encabezado (por ejemplo `IA / 01 | Modelos de lenguaje`) y una regla de 6 px. Las palabras entran con máscara y un movimiento seco.
- **Diagramas en tratamiento Newspaper dibujados con p5.brush 2.2.3** [F-p5brush] (versión exacta fijada): cajas y flechas a pluma, achurado tipo grabado en lugar de semitono, círculos con marcador y un "hervor" (la semilla cambia cada 3 cuadros).
- **rough-notation** solo para subrayar texto HTML.
- **Sin textura de papel de fondo:** el grano infla el archivo y se recomprime mal en Instagram (observado en el spike, Apéndice A).
- **Fuentes locales** (paquetes @fontsource, licencia OFL) cargadas con `@remotion/fonts`. No se depende de Google Fonts en el render.

### 4.2 Flujo de producción
```
lecciones/ ──► salida/guiones/<id>.json ──► reels/: voz.wav ──► voz-limpia.wav + palabras.json ──► reel.mp4 ──► publicados.json ──► sitio/
(MDX)          (guion.v1)                   (grabas)           (ffmpeg + whisper.cpp)              (kit)       (reel-publicado.v1)  (inserta el video)
```

1. **La lección es la única fuente.** `lecciones/` valida y exporta el guion; el reel nunca dice algo que la lección no respalde con una cita, y termina con "Lección completa en…".
2. **Kit visual (`reels/kit/`, interno de reels):** lee los tokens de `estilo.v1`; componentes `Reticula`, `Palabra`, `Diagrama` (p5.brush), `Resaltado` (rough-notation), `Barras`, `Subtitulos` y `CierreFuentes`; plantilla de cuatro tiempos: gancho, idea, ejemplo y cierre. Se puede rehacer por completo sin tocar otro departamento.
3. **Tu voz marca el ritmo:** primero grabas y después se anima.
   - whisper.cpp (local y gratis) transcribe con tiempos por palabra; modelo `large-v3-turbo`, idioma `es` [F-whisper]. Ese modelo requiere builds de whisper.cpp de noviembre de 2024 o posteriores y Remotion 4.0.229 o mayor.
   - Cada animación arranca en el cuadro en que dices su `ancla` (§2.1).
   - Un glosario de correcciones se aplica tras transcribir (términos como "Ollama" o "LoRA"). Las palabras con poca confianza se marcan para revisión en Remotion Studio.
4. **Audio con ffmpeg** [F-ffmpeg]:
   - `highpass` quita retumbes graves.
   - `afftdn` reduce el ruido de fondo.
   - `loudnorm` normaliza el volumen según EBU R128, en dos pasadas para archivos.
   - **Objetivo de volumen:** −14 LUFS integrados, como **ajuste configurable marcado "decisión propia"**. Meta no publica un objetivo oficial para Reels; la cifra solo aparece en fuentes de tipo `apoyo` [F-lufs] (§5.4).
5. **Subtítulos integrados** con `createTikTokStyleCaptions()` de `@remotion/captions`: 2 o 3 palabras a la vez, la palabra actual en rojo, colocados en una zona que no tape la interfaz de Instagram.
6. **Render y verificación:** 1080×1920 a 30 fps, H.264 con AAC. Revisión automática con `ffprobe` de resolución, duración, presencia de audio, volumen y peso.
7. **Publicación del video:** el MP4 se sube como asset de GitHub Releases (fuera del historial de Git) y `publicados.json` registra, por lección, el número congelado del reel, la URL del video y sus `destinos` (Instagram al inicio; cada red nueva es un elemento más).
8. **Publicación en redes por etapas**
   - **Inicio:** a mano desde la app.
   - **Laboratorio del servicio** (lección por defecto en §8): API de publicación de Instagram (cuenta profesional). Se crea un contenedor con `media_type=REELS` y `video_url` pública, se revisa su `status_code` y se publica con `media_publish` [F-ig-pub]. La documentación da 100 publicaciones por API cada 24 h, pero la misma página menciona 50; el límite real se consulta con `content_publishing_limit`.
   - **TikTok (L31):** mientras la app no pase la auditoría, todo lo publicado por API queda en modo privado y solo se puede publicar en cuentas privadas [F-tiktok].
9. **Licencia de Remotion:** gratis para personas, empresas con fines de lucro de hasta 3 empleados y organizaciones sin fines de lucro, incluso con uso comercial [F-remotion]. Si lo usas en tu trabajo y la empresa tiene más de 3 empleados, ella necesita una Company License.

### 4.3 Reglas técnicas para p5.brush dentro de Remotion (aprendidas en el spike)
- **Determinismo:** Remotion renderiza cuadros en paralelo y en desorden. Cada cuadro redibuja todo desde cero con semilla fija: `seed(7 + floor(frame / 3))`.
- `clear()` con el color de fondo opaco del estilo. Con transparencia, el lienzo sale blanco y tapa el fondo y el encabezado, así que el encabezado se dibuja encima.
- `scaleBrushes()` es acumulativo: se llama una sola vez por pestaña.
- El barrido de `arc()` se toma módulo 360; los círculos a mano se dibujan con `spline()`.
- El README no coincide con 2.2.3 (no existe `hatch_brush`; se usa `hatchStyle()`). Por eso la versión se fija exacta.
- La librería no trae tipos: el kit incluye una declaración mínima (`p5brush.d.ts`).
- Render con WebGL: `--gl=swangle` en CPU (lo que usa CI). En la torre se medirá la opción con GPU antes de adoptarla.

### 4.4 Regla de aprendizaje
Cada paso del flujo lo haces primero a mano (`ffmpeg`, `whisper-cli`, `npx remotion render`) y solo después lo envuelves en un script de `pnpm`.

---

## 5. Avance, verificación y política de fuentes

### 5.1 `bitacora/progreso.yaml`
Vive en su propio departamento: el curso se versiona igual para cualquiera; el avance es tu historia. Lo actualizas con un commit; lo valida el contrato `progreso.v1`.

```yaml
lecciones:
  L00:
    estado: dominada          # pendiente | en_curso | lab_verificado | dominada
    inicio: 2026-10-12
    fin: 2026-10-19
    horas: 9.5
    pistas: [0, 1, 0, 2]      # nivel máximo abierto por paso: 0, 1, 2 o "solucion"
    evidencia:
      commit: a1b2c3d         # o url del servicio corriendo, o captura
      reel: https://www.instagram.com/reel/...
    recuerdo: { fecha: 2026-10-19, aciertos: 3 }
    explicacion_60s: true
mejoras:                      # cambios al homelab (§3.3)
  - fecha: 2026-10-20
    que: Switch TL-SG108E con VLAN de laboratorio
    por_que: L02
    evidencia: { commit: b4c5d6e }
```

### 5.2 Qué significa "dominada"
El contrato la rechaza salvo que se cumplan las tres pruebas:
- Evidencia duradera del laboratorio (`commit` o captura; una `url` solo como complemento, §3.3) con la verificación del laboratorio pasada.
- `recuerdo.aciertos == 3` (las 3 preguntas sin mirar).
- `explicacion_60s == true`.

Las preguntas de recuerdo reaparecen en una página de **repasos** a los 7 y a los 30 días de `fin`. El cálculo se hace en el navegador con la fecha del día, porque el sitio es estático.

### 5.3 Medidor de independencia
El sitio grafica `pistas` por lección a lo largo del roadmap, con `solucion` = 3. Es la métrica de tu objetivo de dejar de depender de Claude: debería bajar de una fase a otra. Si sube, toca repasar. El dato lo registras tú, con honestidad.

### 5.4 Política de fuentes
- **Tipos:** `oficial`, `paper`, `libro`, `estandar` y `apoyo`. Toda lección necesita al menos una fuente que no sea `apoyo`. Blogs, foros y videos no oficiales son `apoyo` y nunca la única fuente.
- **Citas verificadas:** cada afirmación técnica importante lleva `<Cita id="…"/>`. La validación falla si una cita apunta a una fuente que la lección no declara o si una fuente declarada nunca se cita.
- **Libros:** edición e ISBN en el catálogo; capítulo en cada cita. Explicación propia y citas textuales cortas.
- **Caducidad:** las fuentes `oficial` y `apoyo` con más de 6 meses desde `verificado` aparecen en un reporte semanal "por re-verificar". Es un aviso, no un bloqueo. Los libros se revisan cuando sale una edición nueva.
- **Claude no es fuente.** Lo que Claude redacte entra solo si lo respalda una fuente citable. Las salidas esperadas de los laboratorios se copian de una ejecución real en tu homelab; nunca se inventan.
- **Revisión independiente:** antes de publicar una lección, un agente que no la escribió compara cada afirmación con su fuente.
- **Analogías de los reels:** simplifican sin deformar; cada una se revisa contra la lección.
- **Datos sin fuente oficial:** se marcan como "decisión propia", nunca como hecho. Ejemplo: el objetivo de −14 LUFS (§4.2).

### 5.5 Cómo se suman libros
**Dónde van:** en `biblioteca/` en la raíz del repo en tu computadora, con el nombre `<isbn>-<titulo-corto>.pdf`. Esa carpeta está en `.gitignore` y nunca sube a GitHub.

**Pasos para sumar un libro**
1. Compras la versión sin DRM y guardas el PDF en `biblioteca/`.
2. En un PR del departamento `lecciones/`, agregas una entrada a `fuentes/catalogo.yaml`: id, título, autores, edición, ISBN, URL oficial de la edición, fecha de verificación y `archivo_local`.
3. Si es lectura base de una fase, agregas su id en `fases.yaml`.
4. Las lecciones que lo necesiten lo citan por id y capítulo, cada una en su propio cambio.

**Impacto en lo demás**
| Parte | Impacto |
|---|---|
| `lecciones/` | Una entrada nueva en el catálogo. Las lecciones existentes no cambian; citarlo es opcional y se hace lección por lección. |
| `sitio/` | Ninguno en su código: muestra el libro en las lecturas y en las fuentes porque lee el catálogo vía contrato. |
| `reels/`, `servicio/`, `infra/`, `bitacora/` | Ninguno. Los reels reciben las fuentes ya resueltas dentro de `guion.v1`. |
| Git y CI | Nada entra al repo; la guarda de CI falla si alguien sube un PDF o EPUB. |
| Respaldos | Como `biblioteca/` no está en Git, entra en tus respaldos 3-2-1 (L04). |
| Claude Code | Lee los PDFs desde `biblioteca/`. Para no leer 900 páginas, `herramientas/extraer-capitulo` saca solo el rango de páginas de un capítulo a texto (`pdftotext -f <inicio> -l <fin>`) en `biblioteca/.extraido/`, también fuera de Git. Un PDF con DRM no se puede leer. |
| Fase 4 (RAG) | `biblioteca/` puede servir de corpus de prueba solo para tu estudio personal, nunca dentro del servicio que vendas. |

---

## 6. Riesgos, manejo de errores y pruebas

### 6.1 Riesgos
| Riesgo | Mitigación |
|---|---|
| El proyecto se alarga y se abandona | Cada fase cierra con algo que funciona. Si una semana sale mal, se hace solo el laboratorio y el reel queda pendiente; nunca más de 3 reels atrasados. |
| Un cambio en un departamento rompe otro | Reglas y guardas de §1.3 y §1.4: sin código compartido, contratos versionados y un departamento por PR. |
| Mejorar el homelab se come el tiempo de estudio | Compras justo a tiempo (§3.2) y mejoras solo cuando una lección las pide o al cerrar una fase (§3.3). |
| Scraping y términos de Instagram | Los Términos de Uso prohíben "accessing or collecting information in an automated way without our express permission" y vender datos obtenidos del servicio [F-ig-tos]. La restricción a la recuperación automatizada se agregó en noviembre de 2021 [F-ota-memo]. El servicio usa **solo la API oficial** con permiso de cada creador, y analiza para cada creador sus propios datos; no vende datos. |
| Meta cambia o retira métricas (ya retiró "impressions" [F-ig-insights]) | La ingesta guarda la respuesta cruda antes de transformarla y se puede reprocesar. Las pruebas usan respuestas grabadas, nunca la API en vivo. |
| Dependencias que cambian (p5.brush, Remotion, Astro) | Versiones exactas con archivo de bloqueo por departamento. Dependabot propone actualizaciones semanales por departamento que solo entran si su CI pasa. |
| Fuga de secretos (tokens de Instagram, llaves de AWS) | Nunca entran a Git. `gitleaks` en `pre-commit` y en CI; `.env` en `.gitignore`. |
| Costos de nube y GPU (Fase 5, L22) | Alertas de presupuesto y `terraform destroy` al terminar cada laboratorio. |
| Derechos de autor | `biblioteca/` en `.gitignore` y CI falla si hay PDF o EPUB en el repo. Fuentes tipográficas OFL. Los reels no llevan música; un audio de tendencia se agrega a mano en la app. |
| Falla de hardware o pérdida de datos | Respaldos 3-2-1 (L04), incluida `biblioteca/`. El repo en GitHub es la copia externa del código. GitHub Pages es el respaldo del sitio. |
| Licencia de Remotion en el trabajo | Ver §4.2, punto 9. |

### 6.2 Manejo de errores
- **Contratos:** si un archivo publicado no cumple su contrato, el error dice el archivo, el campo y la versión del contrato.
- **Lecciones y bitácora:** el validador indica el archivo y el campo exactos.
- **Reels:** cada paso deja su archivo intermedio (`voz-limpia.wav`, `palabras.json`). Si algo falla, se retoma desde el último paso bueno.
- **Servicio:** reintentos con espera creciente ante límites de la API, aviso antes de que caduque un token, y alerta si un cron no se reporta (se monta en L05).

### 6.3 Pruebas en CI (GitHub Actions)
Cada workflow de departamento corre cuando cambian archivos de su carpeta o de un contrato que consume. Las guardas corren en cada PR.

| Workflow | Revisiones |
|---|---|
| `lecciones` | Validador de cabeceras y catálogo; citas (que existan, que se usen, al menos una que no sea `apoyo`); que `salida/guiones/` esté al día y cumpla `guion.v1`. Semanalmente: enlaces externos con `lychee` y reporte de fuentes por re-verificar, que abren un issue en lugar de bloquear. |
| `sitio` | Pruebas de contrato de lo que consume; `astro check` y build; enlaces internos. |
| `reels` | Pruebas de contrato; revisión de tipos y un cuadro fijo por composición con `npx remotion still` (`--gl=swangle`); `publicados.json` cumple `reel-publicado.v1`. No hay renders completos en CI. |
| `bitacora` | `progreso.yaml` cumple `progreso.v1`. |
| `servicio` | `ruff`, `pytest` y pruebas contra respuestas grabadas de la API. Las pruebas de calidad de datos y del modelo se agregan en L08 y L12. |
| `infra` | `terraform fmt -check` y `terraform validate`, `docker compose config` y `shellcheck`. |
| `contratos` | Cada esquema es JSON Schema válido y sus ejemplos válidos e inválidos se comportan como se espera. |
| Guardas (cada PR) | Independencia, alcance del PR (un departamento), `gitleaks` y ausencia de PDF o EPUB. |

**Flujo de trabajo:** `main` protegida. Cada cambio va en una rama con PR y se integra solo si CI pasa, aunque trabajes solo. Las mismas revisiones corren localmente con `pre-commit`.

---

## 7. Fuera de alcance
- After Effects, Adobe o cualquier herramienta de pago para los reels.
- Voz sintética.
- Scraping de Instagram o TikTok.
- Analítica de TikTok al inicio: sus APIs oficiales están orientadas a iniciar sesión, publicar y mostrar videos más que a analítica [F-tiktok-guia]. TikTok entra en L31, por publicación.
- Música agregada por el pipeline.
- Reproductor interactivo de Remotion dentro del sitio (se inserta el video renderizado; ver §1.3).
- Código compartido entre departamentos, incluido un workspace de dependencias común.
- Cuentas de usuario, cobros o plataforma de venta **del curso**; el sitio es estático. Los cobros de L30 son del servicio.
- Renders completos en CI.

---

## 8. Decisiones diferidas (con valor por defecto)
| Decisión | Valor por defecto | Cuándo se confirma |
|---|---|---|
| Proveedor de nube | AWS | Antes de iniciar la Fase 5 |
| Objetivo de volumen | −14 LUFS ("decisión propia") | Se ajusta tras medir los primeros reels |
| Render con GPU en la torre | `--gl=swangle` (CPU) | Tras medir en la torre la opción con GPU |
| Tamaño del modelo de whisper | `large-v3-turbo` | Tras medir velocidad y calidad en la torre |
| Lección donde se automatiza la publicación en Instagram | L25: el almacenamiento en la nube da la URL pública que exige la API | Al planear la Fase 5 |
| Forma del contrato `despliegue.v1` | Nombre de imagen y tag, puerto, variables de entorno requeridas y healthcheck | La primera vez que `infra/` despliega algo de otro departamento |

---

## 9. Cómo se ejecuta este diseño

**Con Claude Code, de la mano.** Los planes se escriben para ejecutarse en Claude Code, un departamento a la vez, abriendo la sesión dentro de la carpeta del departamento. Cada paso del plan indica si lo escribes tú (objetivo de aprendizaje, con pistas escalonadas) o si Claude Code puede generarlo (herramientas que no son objetivo de aprendizaje, como las guardas o el validador); lo generado lo revisas y debes poder explicarlo.

Este diseño cubre unos 7 meses, demasiado para un solo plan. Se ejecuta en sub-proyectos, cada uno con su propio plan (writing-plans) y respetando "un PR, un departamento":

1. **SP1 · Fundación (es el laboratorio L00):** `contratos/` con `leccion.v1`, `progreso.v1` y `estilo.v1`; departamento `lecciones/` (validador, catálogo, `fases.yaml` y la lección L00); departamento `bitacora/`; departamento `sitio/` (Astro + Starlight, mapa y avance); `herramientas/` con las guardas; los `CLAUDE.md`; CI y publicación en GitHub Pages.
2. **SP2 · Pipeline de reels:** contratos `guion.v1` y `reel-publicado.v1`; exportador de guiones en `lecciones/`; departamento `reels/` (kit con p5.brush, voz con ffmpeg y whisper.cpp, subtítulos, render, verificación con `ffprobe`); el sitio inserta el video. Produce el primer reel: "monté mi roadmap como código".
3. **SP3 en adelante · Una fase por sub-proyecto:** las lecciones, laboratorios y código de `servicio/` e `infra/` de cada fase.

---

## 10. Fuentes

Formato: [id] título — tipo — fecha de verificación.

- [F-ig-insights] Instagram Platform: Instagram User Insights — oficial — 2026-10-08 — https://developers.facebook.com/docs/instagram-platform/api-reference/instagram-user/insights
- [F-tiktok-guia] TikTok Developer API: Getting Started Guide (Zernio) — apoyo — 2026-10-08 — https://zernio.com/blog/tiktok-developer-api
- [F-remotion] Remotion License (v4.0.529) — oficial — 2026-10-10 — https://cdn.jsdelivr.net/npm/remotion@4.0.529/LICENSE.md (también https://github.com/remotion-dev/remotion/blob/main/LICENSE.md)
- [F-mkdocs] Material for MkDocs: anuncio de Zensical y modo mantenimiento — oficial — 2026-10-10 — https://squidfunk.github.io/mkdocs-material/blog/2025/11/05/zensical/
- [F-astro-cf] Cloudflare acquires Astro (comunicado de prensa) — oficial — 2026-10-10 — https://www.cloudflare.com/press/press-releases/2026/cloudflare-acquires-astro-to-accelerate-the-future-of-high-performance-web-development/
- [F-starlight] Starlight — oficial — 2026-10-10 — https://starlight.astro.build/
- [F-ddia] Designing Data-Intensive Applications, 2.ª ed. (blog de Martin Kleppmann) — oficial — 2026-10-10 — https://martin.kleppmann.com/2026/03/24/designing-data-intensive-applications-2e.html
- [F-geron] Hands-On Machine Learning with Scikit-Learn and PyTorch (O'Reilly) — oficial — 2026-10-10 — https://oreilly.com/library/view/hands-on-machine-learning/9798341607972/
- [F-aie] AI Engineering, Chip Huyen (WorldCat) — oficial — 2026-10-10 — https://search.worldcat.org/title/1569046080
- [F-hollm] Hands-On Large Language Models (O'Reilly) — oficial — 2026-10-10 — https://www.oreilly.com/library/view/-/9781098150952
- [F-docker] Docker: Up & Running, 3.ª ed. (O'Reilly) — oficial — 2026-10-10 — https://oreilly.com/library/view/docker-up/9781098131814
- [F-terraform] Terraform: Up and Running, 3.ª ed. (O'Reilly) — oficial — 2026-10-10 — https://www.oreilly.com/library/view/terraform-up-and/9781098116736/
- [F-acm] O'Reilly Online Learning para miembros (ACM Learning Center) — oficial — 2026-10-10 — https://learning.acm.org/e-learning/safari
- [F-ebooks] DRM-free O'Reilly ebooks available from eBooks.com (2017) — oficial — 2026-10-10 — https://about.ebooks.com/non-drm-oreilly-ebooks-available-ebooks-com/
- [F-whisper] Remotion: `transcribe()` de @remotion/install-whisper-cpp — oficial — 2026-10-10 — https://www.remotion.dev/docs/install-whisper-cpp/transcribe
- [F-ig-pub] Instagram Platform: Content Publishing — oficial — 2026-10-10 — https://developers.facebook.com/docs/instagram-platform/content-publishing
- [F-tiktok] TikTok for Developers: Content Posting API, Direct Post — oficial — 2026-10-10 — https://developers.tiktok.com/doc/content-posting-api-reference-direct-post
- [F-ffmpeg] FFmpeg Filters Documentation (`loudnorm`, `afftdn`, `highpass`; verificado en `doc/filters.texi` del repositorio oficial) — oficial — 2026-10-11 — https://ffmpeg.org/ffmpeg-filters.html
- [F-ig-tos] Instagram Terms of Use (vigentes desde el 1 de enero de 2025; texto verificado en la copia de Open Terms Archive) — oficial — 2026-10-11 — https://help.instagram.com/581066165581870 · copia: https://github.com/OpenTermsArchive/pga-versions/blob/main/Instagram/Terms%20of%20Service.md
- [F-ota-memo] Instagram blocks data retrieval and clarifies what information it retrieves (Open Terms Archive, nov. 2021) — apoyo — 2026-10-11 — https://opentermsarchive.org/en/memos/instagram-blocks-data-retrieval-and-clarifies-what-information-it-retrieves/
- [F-lufs] Audio Normalization: LUFS Targets by Platform (OpenClip) — apoyo — 2026-10-11 — https://openclip.app/learn/audio-normalization
- [F-p5brush] p5.brush 2.2.3 (MIT, Alejandro Campos Uribe) — oficial — 2026-10-10 — https://github.com/acamposuribe/p5.brush
- [F-cc-memory] Claude Code Docs: How Claude remembers your project (CLAUDE.md) — oficial — 2026-10-11 — https://code.claude.com/docs/en/memory
- [F-psref] Lenovo PSREF: ThinkCentre M75q Gen 5 Spec — oficial — 2026-10-12 — https://psref.lenovo.com/syspool/Sys/PDF/ThinkCentre/ThinkCentre_M75q_Gen_5/ThinkCentre_M75q_Gen_5_Spec.PDF
- [F-cyberpower] CyberPower México: UT1000GU — oficial — 2026-10-12 — https://www.cyberpower.com/mx/es/product/sku/ut1000gu

---

## Apéndice A: resultados del spike de estilo (código desechable)

Medido el 2026-10-10 en el entorno de nube (2 CPU, sin GPU, `--gl=swangle`), con un reel de prueba de 8 s:

| Muestra | Render | Peso |
|---|---|---|
| Swiss | 24 s | 0.3 MB |
| Newspaper (con textura de papel) | 46 s | 4.0 MB |
| Blueprint | 82 s | 0.3 MB |
| Híbrido Swiss + semitono (sin papel) | no medido | 1.2 MB |
| Híbrido con p5.brush (estilo adoptado) | 70 s | 1.9 MB |

Conclusiones: el estilo con p5.brush es viable y determinista en Remotion; tarda más que la versión con semitono, pero es manejable; la textura de papel se descarta por peso. El código del spike no se reutiliza tal cual: sirve de referencia para el kit de `reels/`.
