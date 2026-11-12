# Homelab v2 — Diseño

- **Fecha:** 2026-11-11
- **Estado:** borrador para revisión
- **Autor:** Jair Rangel (diseño asistido por Claude)
- **Reemplaza a:** el diseño del homelab del 2026-10-22. Sus archivos se perdieron antes de subirse a este repo. Aquí se conserva lo que se aprobó y se actualiza el hardware.
- **Alcance de esta versión:** la plataforma que necesita el **primer proyecto de ingesta de datos** (recolectores, carga a la base y vigilancia), más la mudanza al nodo nuevo cuando llegue. Fotos, servicios para clientes y exposición a internet quedan para una versión posterior (§10).
- **Privacidad:** este repo es público. Las cargas de trabajo se describen de forma genérica: "proyecto de ingesta", "proyecto". Los detalles de cada proyecto viven en su propio repo privado.

---

## 0. Qué cambió desde el 2026-10-22

| Antes | Ahora | Por qué |
|---|---|---|
| Laptop `recolector-vigia`: recolectores, cola temporal y vigía | **Fuera del diseño** por ahora | Simplificar: los recolectores corren junto al disco y el vigía, en el mini PC |
| Cola en la laptop más un entregador `rsync` hacia el disco frío | **Sin cola**: el recolector escribe directo en el frío | Recolector y disco quedan en el mismo equipo. La escritura atómica (`*.parcial` y renombrado) protege contra archivos a medias |
| Torre con GPU para trabajos pesados manuales | **Fuera del diseño** | Para no desgastarla. La GPU se mueve al nodo nuevo |
| NAS comercial a futuro | **Nodo nuevo armado a mano**, con espejo ZFS y GPU | Aprovecha piezas existentes (CPU, RAM y GPU) |
| Vigía en un equipo distinto del servidor | Vigía en el mini PC con un **aviso externo de hombre muerto**. Cuando llegue el nodo nuevo, cada equipo vigila al otro | Mientras haya un solo equipo, alguien de fuera debe notar si se cae |
| Sin orquestación de agentes | **n8n** para la vigilancia continua y para que subagentes revisen el proceso, sin ejecutar acciones | Decisión del 2026-11-11 |

**Lo que no cambia:**
- El contrato de 10 reglas por proyecto (§5).
- Los niveles caliente y frío, y "medir, no repartir" los tamaños.
- Las VLAN y Tailscale.
- La política de respaldos con prueba de restauración.
- NUT con el UPS.

## 1. Equipos y roles

| Equipo | Hardware | Rol hoy (tramo 1) | Rol con el nodo nuevo (tramo 2) |
|---|---|---|---|
| **Mini PC** | Lenovo ThinkCentre M75q Gen 5: Ryzen 7 PRO 8700GE (8C/16T), 32 GB DDR5, NVMe (pool `local-lvm` de unos 348 GiB), HDD de 1 TB, Ethernet Gigabit [F-psref] | **Servidor 24×7**: Proxmox VE 9, VM `db`, VM `apps`, VM `vigia` y el HDD de 1 TB como disco frío | **Segundo nodo**: VM `vigia` y el HDD de 1 TB para **respaldos** |
| **Nodo nuevo** (en compra) | Ryzen 7 5700X, 64 GB DDR4, RTX 3060 Ti 8 GB, NVMe de 1 TB (TLC), 2×4 TB CMR, gabinete Jonsbo N3 | — | **Servidor 24×7 principal**: VM `db`, VM `apps`, **espejo ZFS de 2×4 TB como frío** y la GPU para IA local |
| UPS | Alimenta el mini PC, el switch, el módem y después el nodo nuevo | Apagado ordenado con NUT [F-nut] | Igual; revisar que aguante el pico del nodo (~350 W con la GPU) |
| Laptop, torre | — | Fuera | Fuera |

**El BIOS del mini PC ya está configurado:** se enciende solo al volver la luz (*Restore on AC Power Loss = Power On*), verificado con una prueba el 27-oct.

## 2. Datos: niveles y discos

| Nivel | Dónde (tramo 1) | Dónde (tramo 2) | Qué guarda |
|---|---|---|---|
| **Caliente** | NVMe del mini PC (`local-lvm`, thin provisioning) | NVMe del nodo nuevo | Discos de las VMs y la base de datos |
| **Frío** | HDD de 1 TB del mini PC: `/mnt/frio/{crudo,archivo,planes,respaldos}` | Pool ZFS `frio` en espejo de 2×4 TB: mismas carpetas | Respuestas crudas de las APIs (permanentes), archivo Parquet, planes de trabajo |
| **Respaldos** | `/mnt/frio/respaldos`, **el mismo HDD** (riesgo aceptado, §9) | **HDD de 1 TB del mini PC**, otro equipo | vzdump de las VMs y `pg_dump` por esquema |

- **El frío se comparte por NFS** con las VMs de la VLAN de servicios, con `all_squash` al uid y gid **2000**. Así cualquier contenedor que corra como `2000:2000` escribe con el mismo dueño [F-exports]. `respaldos/` **no se exporta**.
- **"Medir, no repartir":** no se asignan cuotas por servicio de antemano. Cada proyecto declara en `niveles.yaml` el tamaño **medido** durante su periodo en paralelo, y la plataforma vigila el uso con alertas: thin pool al 80 %, frío al 80 %.
- **Los discos de las VMs solo crecen.** Se empieza chico y se amplía con `qm resize` cuando la medición lo pida [F-pve-storage].

## 3. Red

- **VLAN 20 (servicios, 10.0.20.0/24):** VMs y contenedores. La puerta de enlace es `10.0.20.1` en `vmbr0.20` del host Proxmox, con NAT hacia la red de la casa.
- **VLAN 30 (clientes)** y **VLAN 40 (datos)**: como en el diseño original, sin cambios en esta versión.
- **Direcciones fijas en la VLAN 20:**

| Nombre | IP | Qué es |
|---|---|---|
| `db` | 10.0.20.11 | VM, PostgreSQL 17 |
| `apps` | 10.0.20.12 | VM, Docker: recolectores, cargas y procesamiento de los proyectos |
| `vigia` | 10.0.20.20 | VM, Docker: Prometheus, Alertmanager, Pushgateway, node_exporter y n8n |

- **Salida a internet:** por la conexión de la casa. Algunas fuentes de datos rechazan IP de centro de datos, así que **los recolectores deben correr en casa**, nunca en la nube.
- **Acceso remoto: Tailscale**, como *subnet router* en el host, sin abrir puertos en el módem [F-tailscale]. También da acceso a un equipo externo de solo lectura durante las migraciones.
- **Nada expuesto a internet** en esta versión (regla 9).

## 4. Cómputo

| VM | vCPU | RAM inicial | Disco inicial | Notas |
|---|---|---|---|---|
| `db` | 4 | 8 GB | 64 GB | PostgreSQL 17, servicio compartido: **un esquema y un rol dueño por departamento de cada proyecto**, más roles de solo lectura |
| `apps` | 6 | 16 GB | 64 GB | Docker; cada servicio con `mem_limit` y `cpus`. Monta `crudo/`, `archivo/` y `planes/` por NFS **con escritura** |
| `vigia` | 2 | 3 GB | 32 GB | Docker: Prometheus, Alertmanager, Pushgateway, node_exporter y n8n |

- **Total en el mini PC:** 27 GB de 32. Queda margen para el host, pero no para crecer: **la RAM es el recurso a vigilar**. Un proyecto que pida más de unos 12 GB para un solo job espera al nodo nuevo.
- **Horarios:** los jobs se programan con **temporizadores de systemd** en `apps` (con recuperación de corridas perdidas), no con n8n ni con cron.

## 5. Contrato por proyecto (las 10 reglas)

1. **Tres piezas:** recolector (pide y guarda), procesamiento (transforma y carga) y pesado (cuando haga falta GPU o mucha memoria).
2. **Niveles declarados** en `deploy/homelab/niveles.yaml`, con tamaños medidos.
3. **`deploy/homelab/compose.yml`** con perfiles (`recolector`, `procesamiento`, `pesado`) y su Dockerfile.
4. **Configuración solo por variables de entorno:** `PROYECTO`, `EQUIPO`, `DATABASE_URL`, `CRUDO_DIR`, `ARCHIVO_DIR`, `PLAN_DIR`, `PUSHGATEWAY_URL` y las claves del proyecto, que se documentan **solo por nombre**.
5. **Jobs idempotentes:** correr dos veces no duplica ni cambia el resultado.
6. **Latido** a Pushgateway por **POST** al terminar cada job, con `intervalo_max_s` igual al hueco más largo entre corridas más plazo y holgura. **Solo el código 0 es éxito** [F-pushgateway].
7. **Límites de recursos** (`mem_limit` y `cpus`) en cada servicio.
8. **`RESTAURAR.md` por pieza**, que se pueda seguir en limpio.
9. **Cerrado por defecto:** sin puertos publicados que no se necesiten.
10. **El perfil pesado acepta `--muestra`** y se prueba en CI con pocos datos.

## 6. Vigilancia

```
jobs en apps ──POST──► Pushgateway ─┐
node_exporter (host y VMs) ─────────┼─► Prometheus ─► Alertmanager ─► Telegram
                                     │                     │
                                     │                     └─► "Watchdog" cada 5 min ─► Healthchecks.io
                                     │                                                    (si deja de llegar,
                                     │                                                     avisa por correo/Telegram)
                                     └─► n8n (solo lectura) ─► resumen diario + subagente que investiga alertas
```

- **Reglas base:**
  - `JobFallo`: el último resultado fue 0.
  - `JobSinSenal`: pasó más de `intervalo_max_s` desde el último éxito.
  - `EquipoCaido`.
  - Thin pool o frío al 80 % o más.
  - SMART en mal estado.
  - UPS en batería.
  - Edad de los respaldos.
- **Aviso externo de hombre muerto:** una alerta `Watchdog` que siempre está disparada se envía cada 5 minutos a un *check* de Healthchecks.io. Si el mini PC o el vigía se caen, el ping deja de llegar y **el servicio externo avisa** [F-am-config] [F-watchdog] [F-healthchecks]. Es lo que cubre el hueco de tener un solo equipo.
- **n8n** [F-n8n]:
  - Lee Alertmanager, Prometheus y la base **con un rol de solo lectura**.
  - Arma un resumen diario y, ante una alerta, lanza un subagente que investiga (logs, manifiestos, vigilancias) y **propone** qué hacer.
  - **No lanza jobs, no escribe en las bases y no ejecuta arreglos.** Las acciones las decide una persona.
  - Sus claves viven en el `.env` de `vigia`.
- **Con el nodo nuevo:** `vigia` se queda en el mini PC y el trabajo se va al nodo nuevo, así que cada equipo vigila al otro. El aviso externo se queda como tercera línea.

## 7. Respaldos y restauración

| Qué | Cómo | Retención |
|---|---|---|
| VMs | **vzdump** diario al almacenamiento `respaldos` [F-pve-backup] | 7 diarios y 4 semanales |
| Bases | **`pg_dump` diario por esquema** (`-n <esquema>`, formato *custom*) [F-pgdump] | 14 días |
| Configuración del host | `/etc/pve`, la red y los timers, en un tar diario dentro de `respaldos` | 14 días |
| Crudo y archivo | **Sin segunda copia** en el tramo 1 (§9). En el tramo 2 viven en el espejo ZFS | Permanente |

- **Prueba de restauración mensual, automática:** restaura el último vzdump de `db` en una VM temporal sin red, restaura un `pg_dump`, cuenta filas contra el original y borra la VM. El resultado va al vigía como un latido más.
- **La mudanza al nodo nuevo (§8) es una restauración real** de todas las VMs, y cuenta como prueba.

## 8. Tramo 2: el nodo nuevo

1. **Armado y BIOS:**
   - Primero fuera del gabinete, verificando que dé video.
   - BIOS actualizado, *Restore on AC Power Loss = Power On* y perfil de memoria activo.
   - MemTest86 con los 64 GB.
2. **Proxmox VE 9** en el NVMe y el **pool ZFS `frio`** en espejo con los 2×4 TB [F-pve-zfs].
3. **Mudanza:**
   - Se detienen los timers y se hace un vzdump final de `db`, `apps` y `vigia`.
   - `db` y `apps` se restauran en el nodo nuevo y el contenido del frío se copia al pool ZFS.
   - Se verifican conteos y sha256 del crudo, y se reactivan los timers.
   - `vigia` se queda en el mini PC.
4. **Respaldos:** el almacenamiento `respaldos` pasa al HDD de 1 TB del mini PC.
5. **GPU:**
   - El driver de NVIDIA se instala en el host y un contenedor LXC usa la GPU (Ollama y modelos de visión).
   - El driver queda cargado para que la GPU baje a su consumo de reposo.
   - Los proyectos la piden con el perfil `pesado`.
6. **Sin clúster de Proxmox por ahora:** un clúster de dos nodos pierde el quórum si uno se cae, salvo que haya un tercer voto (QDevice) [F-pve-cluster] [F-qdevice]. Los dos nodos quedan independientes y se mueven VMs con vzdump. El clúster se reconsidera cuando haya un tercer voto.

## 9. Riesgos aceptados

1. **En el tramo 1, frío y respaldos comparten el HDD de 1 TB.** Si muere ese disco, se pierden el crudo y los respaldos a la vez. Mitigación: el tramo 2 los separa en equipos distintos, y hasta entonces SMART está vigilado.
2. **El crudo no tiene copia fuera de casa.** Una copia externa (otro disco o la nube) se decide después del tramo 2.
3. **Un solo equipo en el tramo 1:** si se cae el mini PC, se cae todo. El aviso externo garantiza que te enteres, no que siga funcionando.
4. **RAM ajustada en el mini PC** (§4).
5. **El cable USB del UPS sigue pendiente:** sin él, NUT no puede leer el estado de la batería. Hasta que se conecte, un corte largo apaga los equipos de golpe.

## 10. Fuera de esta versión

- Fotos al estilo iCloud (Immich), servicios para clientes, Cloudflare Tunnel y cualquier exposición a internet.
- El equipo externo de solo lectura para migraciones es temporal y se retira al terminar cada migración.
- El rack de 10" propio (perfil de aluminio 2020 con piezas impresas en 3D): proyecto físico aparte.

## 11. Fuentes

> Las URL oficiales no se pudieron abrir desde la sesión que redactó este spec (red restringida). Verifícalas al revisar; F-watchdog y F-qdevice salieron de búsqueda web el 2026-11-11.


- **[F-psref]** Lenovo PSREF, ThinkCentre M75q Gen 5 — https://psref.lenovo.com/Product/ThinkCentre/ThinkCentre_M75q_Gen_5
- **[F-pve-backup]** Proxmox VE, *Backup and Restore* — https://pve.proxmox.com/wiki/Backup_and_Restore
- **[F-pve-storage]** Proxmox VE, *Storage* — https://pve.proxmox.com/wiki/Storage
- **[F-pve-zfs]** Proxmox VE, *ZFS on Linux* — https://pve.proxmox.com/wiki/ZFS_on_Linux
- **[F-pve-cluster]** Proxmox VE, *Cluster Manager* (quórum y QDevice) — https://pve.proxmox.com/wiki/Cluster_Manager
- **[F-pgdump]** PostgreSQL 17, `pg_dump` — https://www.postgresql.org/docs/17/app-pgdump.html
- **[F-pushgateway]** Prometheus Pushgateway (semántica de POST y PUT) — https://github.com/prometheus/pushgateway
- **[F-am-config]** Prometheus Alertmanager, configuración — https://prometheus.io/docs/alerting/latest/configuration/
- **[F-watchdog]** PromLabs, *End-to-End Watchdog Alerts* — https://training.promlabs.com/training/monitoring-and-debugging-prometheus/metrics-based-meta-monitoring/end-to-end-watchdog-alerts/
- **[F-qdevice]** WZ-IT, *Proxmox two-node cluster with a QDevice* — https://wz-it.com/en/knowledge/proxmox/two-node-cluster-qdevice/
- **[F-healthchecks]** Healthchecks.io, documentación — https://healthchecks.io/docs/
- **[F-n8n]** n8n, *Hosting* — https://docs.n8n.io/hosting/
- **[F-tailscale]** Tailscale, *Subnet routers* — https://tailscale.com/kb/1019/subnets
- **[F-exports]** `exports(5)`, opciones de NFS (`all_squash`, `anonuid`) — https://man7.org/linux/man-pages/man5/exports.5.html
- **[F-nut]** Network UPS Tools, manual de usuario — https://networkupstools.org/docs/user-manual.chunked/index.html
