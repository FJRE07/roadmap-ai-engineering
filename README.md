# Roadmap AI Engineering

Soy data scientist y este repositorio es mi camino, en público, de homelab a
AI Engineering, MLOps y Cloud. Cada tema produce tres piezas: una lección con
fuentes citables, un laboratorio práctico y un reel que lo explica con
analogías sencillas. Los laboratorios construyen, paso a paso, un servicio de
inteligencia de contenido para creadores de Reels: primero Instagram, después
TikTok. Todo vive como código: el contenido, el sitio, los reels, el servicio
y la infraestructura.

## Estructura

El repositorio está dividido en departamentos independientes. Ninguno usa
código de otro: solo se leen archivos publicados que cumplen un contrato
versionado en `contratos/`.

| Carpeta | Qué contiene |
|---|---|
| `contratos/` | Esquemas versionados: lo único que comparten los departamentos |
| `lecciones/` | Lecciones en MDX, catálogo de fuentes y fases |
| `sitio/` | Sitio web con Astro + Starlight: mapa, lecciones y avance |
| `reels/` | Producción de reels con Remotion |
| `servicio/` | El producto, en Python |
| `infra/` | Homelab (Proxmox, Docker) y después la nube (Terraform) |
| `bitacora/` | Mi avance: lecciones, evidencias y mejoras al homelab |
| `herramientas/` | Guardas que hacen cumplir las reglas del repo |
| `docs/` | Diseño y planes de implementación |

Las carpetas se van creando conforme avanza el plan.

## Reglas

- Un PR toca un solo departamento.
- Toda afirmación técnica de una lección lleva una fuente citable.
- Nada de libros (PDF/EPUB) ni secretos en el repositorio.

## Documentos

- [Spec de diseño](docs/superpowers/specs/2026-10-11-roadmap-ai-engineering-design.md)
- [Plan de la fundación (L00)](docs/superpowers/plans/2026-10-12-sp1-fundacion-l00.md)
