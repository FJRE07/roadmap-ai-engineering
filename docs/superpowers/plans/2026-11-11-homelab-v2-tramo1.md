# Homelab v2 · Tramo 1 (Paso 0 en el mini PC) — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** dejar el mini PC listo para recibir proyectos en producción.
- Red de servicios.
- Disco frío compartido.
- VMs `db`, `apps` y `vigia`.
- Alertas a Telegram con aviso externo de hombre muerto y n8n de solo lectura.
- Respaldos con prueba de restauración.
- Tailscale y NUT.

**Architecture:** Proxmox VE 9 en el mini PC, con tres VMs Debian 13 en la VLAN 20 (10.0.20.0/24). La puerta de enlace y el NAT viven en el host. El HDD de 1 TB es el disco frío: `crudo/`, `archivo/` y `planes/` se exportan por NFS como 2000:2000, y `respaldos/` es almacenamiento local de Proxmox. Lo que se puede probar (inventario, métricas del host y reglas de alertas) vive en el departamento `infra/` con pruebas; lo demás son pasos guiados en el equipo con su verificación.

**Tech Stack:** Proxmox VE 9 · Debian 13 (trixie) · PostgreSQL 17 · Docker Engine · NFS (`nfs-kernel-server`) · Prometheus · Alertmanager · Pushgateway · node_exporter · n8n · Healthchecks.io · Tailscale · NUT · Python 3.12 con uv (pytest, ruff, PyYAML). **Las versiones de imágenes y paquetes se fijan al ejecutar cada tarea**, consultando su página oficial ese día, y se anotan en el commit.

**Spec:** `docs/superpowers/specs/2026-11-11-homelab-v2-design.md`. Léela junto con este plan.

## Cómo se ejecuta este plan

- **Lo ejecutas tú, de la mano con Claude:** en el chat para los pasos en el equipo, y con Claude Code en `infra/` para el código.
- **Marcas de cada paso:**
  - **[Guía]**: configuración en el equipo, con recorrido completo.
  - **[Claude Code]**: lo genera Claude Code y tú lo revisas antes del commit.
  - **[Tú]**: objetivo de aprendizaje; solo se dan pistas de nivel 1 y 2.
- **Dónde se corre cada paso:** `(host)` es la consola del mini PC (`ssh root@192.168.100.50`); `(db)`, `(apps)` y `(vigia)` son las VMs; `(WSL)` es tu repo local.
- **Flujo de PR (igual que en SP1):** rama por tarea, `gh pr create --fill`, checks en verde, `gh pr merge --squash --delete-branch`. Un PR toca solo `infra/`.
- **Regla de evidencia:** cada `Expected:` se compara con la salida real, y lo verificado se pega en el PR. **Claude no es fuente:** los comandos de configuración se contrastan con la documentación oficial citada en la spec (§11).

## Global Constraints

- **Direcciones:** el host es `192.168.100.50` en la LAN de la casa y `10.0.20.1/24` en `vmbr0.20`. `db` = `10.0.20.11`, `apps` = `10.0.20.12`, `vigia` = `10.0.20.20`.
- **Recursos de las VMs:**

| VM | vCPU | RAM | Disco |
|---|---|---|---|
| `db` | 4 | 8 GB | 64 GB |
| `apps` | 6 | 16 GB | 64 GB |
| `vigia` | 2 | 3 GB | 32 GB |

  Los discos solo crecen, con `qm resize`.
- **Disco frío:**
  - Se monta en `/mnt/frio` **por UUID**, con las carpetas `crudo/`, `archivo/`, `planes/` y `respaldos/`.
  - Se exportan `crudo/`, `archivo/` y `planes/` a `10.0.20.0/24` con `rw,sync,all_squash,anonuid=2000,anongid=2000,no_subtree_check`. **`respaldos/` no se exporta.**
  - En `apps`, el montaje es `/srv/frio/<carpeta>`, con `_netdev`.
- **Usuario de datos:** uid y gid `2000` (nombre `datos`) en `apps`; los contenedores corren como `2000:2000`.
- **Respaldos:**
  - vzdump diario con `keep-daily=7,keep-weekly=4` al almacenamiento `respaldos` (`/mnt/frio/respaldos`).
  - `pg_dump -Fc -n <esquema>` diario, con 14 días de retención.
  - Tar diario de `/etc/pve` y `/etc/network`, con 14 días de retención.
  - Prueba de restauración mensual.
- **Métricas de la plataforma** (las que leen las reglas y las pruebas):
  - `homelab_job_ultimo_resultado`, `homelab_job_ultimo_exito_timestamp`, `homelab_job_intervalo_maximo_segundos` (de los jobs, vía Pushgateway con POST).
  - `homelab_thin_uso_ratio`, `homelab_frio_uso_ratio`, `homelab_frio_montado`, `homelab_smart_ok`, `homelab_respaldo_edad_segundos{tipo}`, `homelab_ups_en_bateria` (del host, por el *textfile collector* de node_exporter).
- **Alertas:** `JobFallo`, `JobSinSenal`, `EquipoCaido`, `ThinPoolLleno` y `FrioLleno` (≥ 0.80), `FrioDesmontado`, `SmartMal`, `RespaldoViejo` (vzdump > 26 h, pg > 26 h), `UpsEnBateria` y `Watchdog` (siempre activa).
  - Telegram para todas menos `Watchdog`.
  - `Watchdog` va a Healthchecks.io con `repeat_interval: 5m`.
- **n8n:** solo lectura. Rol de base `lector_vigia` (`SELECT` en los esquemas que se le otorguen). Lee Alertmanager y Prometheus por su API. **No lanza jobs ni escribe en ninguna base.**
- **Secretos solo por nombre:** `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `HEALTHCHECKS_PING_URL`, `ANTHROPIC_API_KEY` (subagente de n8n), `N8N_ENCRYPTION_KEY` y `TS_AUTHKEY`. Viven en el `.env` de cada VM (modo 600) o en `/root/.secretos` en el host, **nunca en Git**.
- **Nada expuesto a internet.** Ningún puerto abierto en el módem.

## Review Focus

1. **El HDD se desmonta y los jobs escriben en el disco del sistema:** si `/mnt/frio` no está montado, el directorio vacío del punto de montaje acepta escrituras y llena el NVMe en silencio. → `homelab_frio_montado` y la alerta `FrioDesmontado`, más la prueba `test_frio_no_montado_es_cero` (Tarea 6). Además, el `exportfs` y el vzdump se niegan a correr sin el montaje: `is_mountpoint` en el almacenamiento (Tarea 3).
2. **Respaldos que "corren" pero no sirven:** un vzdump con código 0 pero vacío, o un `pg_dump` de un esquema que no existe. → La prueba de restauración mensual cuenta filas contra el original (Tarea 8), y `RespaldoViejo` mira la **fecha del archivo más reciente**, no el log (`test_edad_respaldo_toma_el_mas_reciente`, Tarea 6).
3. **Alerta que nunca llega:** un token de Telegram mal copiado deja todo "verde" en silencio. → Cada receptor se prueba con un simulacro real (Tareas 7 y 9), y las reglas tienen pruebas con `promtool test rules` (Tarea 7).
4. **n8n con más permisos de los acordados:** un rol con `INSERT` o un nodo "Execute Command" habilitado rompen la regla de solo lectura. → La Tarea 9 verifica que `lector_vigia` falla al escribir (`ERROR: permission denied`) y desactiva el nodo `executeCommand` con `NODES_EXCLUDE`.
5. **Pérdida de luz larga sin NUT:** sin el cable USB, el UPS no avisa y todo se apaga de golpe. → La Tarea 11 queda **bloqueada** hasta tener el cable, y el riesgo se anota en el inventario (`ups.monitoreado: false`). No se finge.

---

### Task 1: Departamento `infra/` e inventario validado

**Files:**
- Create: `infra/departamento.yaml`, `infra/README.md`, `infra/CLAUDE.md`, `infra/pyproject.toml`, `infra/uv.lock`, `infra/.gitignore`
- Create: `infra/inventario.yaml`
- Create: `infra/src/homelab/__init__.py`, `infra/src/homelab/inventario.py`
- Test: `infra/tests/test_inventario.py`
- Modify: `.github/workflows/` (agregar el job de `infra/`, con el mismo patrón que `herramientas/`)

**Interfaces:**
- Produces:
  - `cargar(ruta: Path) -> dict` (lee el YAML).
  - `validar(inv: dict) -> list[str]` (lista de errores; vacía si es válido).
  - El script `infra-validar` = `homelab.inventario:main`, que sale con 1 si hay errores.
  - `inventario.yaml` con las claves `nodos`, `vms`, `red`, `discos`, `almacenamientos` y `ups`. Es la superficie pública de `infra/`.

- [ ] **Step 1 [Claude Code]:** esqueleto del departamento, igual que `herramientas/`. `departamento.yaml` queda con `nombre: infra`, `publica: [inventario.yaml]` y `consume: []`.
- [ ] **Step 2 [Claude Code]:** `inventario.yaml` con los valores de Global Constraints. Debe incluir:
  - el nodo `minipc` (ThinkCentre M75q Gen 5, `192.168.100.50`);
  - las 3 VMs con IP, vCPU, RAM y disco;
  - la VLAN 20 con su puerta de enlace;
  - el disco frío con su UUID, que se rellena en la Tarea 3;
  - los almacenamientos `local-lvm` y `respaldos`;
  - `ups: {modelo: <pendiente>, monitoreado: false}`.
- [ ] **Step 3 [Tú]: pruebas de `validar`.**
  - `test_inventario_real_es_valido`: el archivo del repo da `[]`.
  - `test_ip_fuera_de_la_vlan`: una VM con `10.0.30.5` da un error que nombra la VM.
  - `test_ips_repetidas`: dos VMs con la misma IP dan un error.
  - `test_ram_excede_el_nodo`: la suma de RAM de las VMs es mayor que la RAM del nodo menos 4 GB de reserva para el host, y da un error.
  - `test_uuid_pendiente_es_aviso_no_error`: el UUID con valor `<pendiente>` no invalida.
- [ ] **Step 4:** corre `uv run pytest -q` en `infra/`. Expected: FAIL (módulo inexistente).
- [ ] **Step 5 [Tú]:** implementa `validar` hasta que pasen.
- [ ] **Step 6:** corre `uv run pytest -q && uv run infra-validar inventario.yaml`. Expected: todas pasan; `infra-validar` sale con 0.
- [ ] **Step 7:** commit y PR: `infra: departamento e inventario validado`.

---

### Task 2: Red de servicios (VLAN 20 y NAT en el host)

**Files:**
- Modify (host): `/etc/network/interfaces`. Se guarda una copia en `infra/host/interfaces` sin secretos.

- [ ] **Step 1 [Guía] (host):** respalda `/etc/network/interfaces` con `cp /etc/network/interfaces /root/interfaces.$(date +%F)`.
- [ ] **Step 2 [Guía] (host):** activa `bridge-vlan-aware yes` en `vmbr0` y agrega la interfaz `vmbr0.20` con `address 10.0.20.1/24`. En `post-up` van el reenvío de IP (`net.ipv4.ip_forward=1`) y el NAT de `10.0.20.0/24` hacia `vmbr0`: masquerade con `nftables`. Aplica con `ifreload -a`.
- [ ] **Step 3 [Guía] (switch):** el puerto del mini PC debe llevar la VLAN 20 *tagged*. Si el switch es el TP-Link SG108E, se hace en *802.1Q VLAN*. Si el switch no está entre el mini PC y nada más, este paso se salta y se anota.
- [ ] **Step 4: verifica** (host): `ip -br addr show vmbr0.20` → `10.0.20.1/24 UP`, y `sysctl net.ipv4.ip_forward` → `= 1`. La prueba completa (que una VM salga a internet) se hace en la Tarea 4.
- [ ] **Step 5:** copia el archivo a `infra/host/interfaces` y haz commit: `infra: red de servicios VLAN 20`.

---

### Task 3: Disco frío y NFS

**Files:**
- Create: `infra/host/preparar-frio.sh`, `infra/host/exports`

- [ ] **Step 1 [Guía] (host): mira el disco antes de tocarlo.** `lsblk -f` y `ls -la /mnt/frio 2>/dev/null`. **ALTO:** si el HDD tiene particiones con datos, **no lo formatees**. Muéstrame la salida y decidimos. Formatear es irreversible.
- [ ] **Step 2 [Claude Code]: `preparar-frio.sh <dispositivo>`.**
  - Exige confirmación escrita (`escribe FORMATEAR`).
  - Formatea ext4 con la etiqueta `frio`.
  - Monta por UUID en `/mnt/frio` (`/etc/fstab` con `nofail`).
  - Crea `crudo/`, `archivo/`, `planes/` y `respaldos/`.
  - Hace `chown 2000:2000` de las tres primeras.
  - Imprime el UUID.
- [ ] **Step 3 [Guía] (host):** corre el script (si el Step 1 lo permitió), anota el UUID en `inventario.yaml` y reinicia el host. Expected: `findmnt /mnt/frio` muestra el disco tras el reinicio.
- [ ] **Step 4 [Guía] (host): NFS.**
  - `apt install nfs-kernel-server`.
  - `/etc/exports` con las 3 líneas de Global Constraints, y `exportfs -ra`.
  - Agrega a `nfs-server.service` un `RequiresMountsFor=/mnt/frio`, con `systemctl edit`.
  - Expected: `exportfs -v` lista las 3 carpetas con `all_squash,anonuid=2000`.
- [ ] **Step 5 [Guía] (host): almacenamiento de respaldos.**
  - `pvesm add dir respaldos --path /mnt/frio/respaldos --content backup --is_mountpoint /mnt/frio --prune-backups keep-daily=7,keep-weekly=4`.
  - Expected: `pvesm status` muestra `respaldos` como `active`.
  - Con el disco desmontado debe salir `inactive`: pruébalo con `umount /mnt/frio`, revisa y vuelve a montar.
- [ ] **Step 6:** commit: `infra: disco frío, NFS y almacenamiento de respaldos`.

---

### Task 4: VM `db` (PostgreSQL 17)

**Files:**
- Create: `infra/host/crear-vm.sh`, `infra/db/crear-base.sh`

**Interfaces:**
- Produces:
  - `crear-vm.sh <vmid> <nombre> <ip> <vcpu> <ram_mb> <disco_gb>`: VM Debian 13 desde la imagen *genericcloud* oficial, con cloud-init (usuario, tu llave SSH, IP fija en `vmbr0` tag 20, gateway `10.0.20.1`) y `qemu-guest-agent`. La reusan las Tareas 5 y 6.
  - `crear-base.sh <proyecto>`: crea la base `<proyecto>` y el rol dueño `<proyecto>_migrador`, sin otros esquemas (cada proyecto crea los suyos con sus migraciones). También crea el rol `lector_vigia` si no existe.

- [ ] **Step 1 [Claude Code]:** `crear-vm.sh`. La imagen y su checksum salen de `cloud.debian.org`, con la versión anotada.
- [ ] **Step 2 [Guía] (host):** `crear-vm.sh 111 db 10.0.20.11 4 8192 64`. Expected: `qm agent 111 ping` responde. Desde `(db)`, `ping -c1 1.1.1.1` funciona, lo que confirma el NAT de la Tarea 2.
- [ ] **Step 3 [Guía] (db):**
  - `apt install postgresql` (en trixie es la versión 17; confírmalo con `psql --version`).
  - `listen_addresses = 'localhost,10.0.20.11'`.
  - `pg_hba.conf` acepta `10.0.20.0/24` solo con `scram-sha-256`.
- [ ] **Step 4 [Claude Code]:** `crear-base.sh`. Las contraseñas se generan y **se imprimen una sola vez** para guardarlas en el `.env` de quien las use.
- [ ] **Step 5: verifica.**
  - Desde el host (`apt install postgresql-client`): `psql -h 10.0.20.11 -U lector_vigia -c 'select 1'` da `1`.
  - `psql … -c 'create table x(i int)'` da `permission denied`.
- [ ] **Step 6:** actualiza `inventario.yaml` (vmid 111) y haz commit: `infra: VM db con PostgreSQL 17`.

---

### Task 5: VM `apps` (Docker y frío montado)

- [ ] **Step 1 [Guía] (host):** `crear-vm.sh 112 apps 10.0.20.12 6 16384 64`.
- [ ] **Step 2 [Guía] (apps):** Docker Engine desde el repositorio oficial de Docker para Debian (no `docker.io` de Debian). Crea el usuario `datos` con uid y gid 2000, y `/srv/stacks`.
- [ ] **Step 3 [Guía] (apps):** `apt install nfs-common`. En `/etc/fstab`, los tres montajes `10.0.20.1:/mnt/frio/<carpeta> /srv/frio/<carpeta> nfs defaults,_netdev,nofail 0 0`.
- [ ] **Step 4: verifica** (apps):
  - `docker run --rm --user 2000:2000 -v /srv/frio/crudo:/x busybox sh -c 'touch /x/.p && ls -ln /x/.p && rm /x/.p'` muestra el dueño `2000 2000`.
  - En el host, `ls -ln /mnt/frio/crudo` no deja nada.
- [ ] **Step 5:** actualiza el inventario y haz commit: `infra: VM apps con Docker y frío`.

---

### Task 6: Métricas del host

**Files:**
- Create: `infra/src/homelab/metricas.py`, `infra/host/metricas-host.service`, `infra/host/metricas-host.timer`
- Test: `infra/tests/test_metricas.py`, con muestras reales de salida en `infra/tests/datos/`

**Interfaces:**
- Produces:
  - `uso_thin(salida_lvs: str) -> float`: de `lvs --noheadings -o data_percent pve/data`; devuelve una fracción.
  - `uso_frio(salida_df: str) -> float`.
  - `frio_montado(salida_findmnt: str) -> int`.
  - `smart_ok(salida_smartctl: str) -> int`: de `smartctl -H`.
  - `edad_respaldo(rutas_y_mtimes: list[tuple[str, float]], ahora: float) -> float`: edad del archivo **más reciente**; `inf` si no hay.
  - `ups_en_bateria(salida_upsc: str | None) -> int | None`: `OB` en `ups.status` es 1. Con `OL DISCHRG`, también 1. Sin NUT, `None` y la métrica no se emite.
  - `formatear(metricas: dict) -> str`: formato de texto de Prometheus.
  - Script `metricas-host`, que escribe atómicamente a `/var/lib/node_exporter/textfile/homelab.prom`.

- [ ] **Step 1 [Guía] (host): captura muestras reales** de `lvs`, `df -B1 /mnt/frio`, `findmnt /mnt/frio`, `smartctl -H /dev/sdX` y una salida de `upsc` (si no hay UPS, escribe la de ejemplo de la documentación de NUT y márcala como tal). Guárdalas en `infra/tests/datos/`.
- [ ] **Step 2 [Tú]: pruebas.**
  - `test_uso_thin`: la muestra real da su porcentaje / 100.
  - `test_frio_no_montado_es_cero`: un `findmnt` vacío da `0`.
  - `test_smart_fallo`: `FAILED` da `0`.
  - `test_edad_respaldo_toma_el_mas_reciente`: con 3 archivos, la edad usa el más nuevo.
  - `test_sin_respaldos_es_infinito`.
  - `test_ups_on_line_discharging_cuenta_como_bateria`.
  - `test_formatear_un_valor_por_linea`.
- [ ] **Step 3:** corre `uv run pytest tests/test_metricas.py -q`. Expected: FAIL.
- [ ] **Step 4 [Claude Code]:** implementa hasta que pasen. Agrega el `.service` y el `.timer` (cada 5 min).
- [ ] **Step 5 [Guía] (host):** instala node_exporter en el host y en las tres VMs con `--collector.textfile.directory=/var/lib/node_exporter/textfile` (solo en el host hace falta el directorio). Instala `metricas-host` y su timer. Expected: `curl -s localhost:9100/metrics | grep homelab_` muestra las métricas.
- [ ] **Step 6:** commit: `infra: métricas del host`.

---

### Task 7: VM `vigia`: Prometheus, Alertmanager, Pushgateway y aviso externo

**Files:**
- Create: `infra/vigia/compose.yml`, `infra/vigia/prometheus.yml`, `infra/vigia/reglas.yml`, `infra/vigia/alertmanager.yml.plantilla`, `infra/vigia/pruebas-reglas.yml`

- [ ] **Step 1 [Guía] (host):** `crear-vm.sh 120 vigia 10.0.20.20 2 3072 32` y Docker como en la Tarea 5.
- [ ] **Step 2 [Claude Code]: `compose.yml`.**
  - Prometheus (retención de 30 días), Alertmanager y Pushgateway, con versiones fijadas el día de la tarea.
  - Pushgateway publicado solo en `10.0.20.20:9091`; Prometheus y Alertmanager solo en `127.0.0.1` y la VLAN 20.
  - `restart: unless-stopped` y `mem_limit` en cada servicio.
- [ ] **Step 3 [Tú]: `reglas.yml`** con las 10 alertas de Global Constraints. `JobSinSenal` usa `time() - homelab_job_ultimo_exito_timestamp > homelab_job_intervalo_maximo_segundos`.
- [ ] **Step 4 [Claude Code]: `pruebas-reglas.yml`** para `promtool test rules`.
  - `JobFallo` se dispara con resultado 0.
  - `JobSinSenal` se dispara pasado el intervalo y **no** antes.
  - `FrioDesmontado` se dispara con `homelab_frio_montado 0`.
  - `RespaldoViejo` se dispara a las 27 h.
  - `Watchdog` está siempre activa.
- [ ] **Step 5:** corre `docker run --rm -v $PWD:/w --entrypoint promtool prom/prometheus:<versión> test rules /w/pruebas-reglas.yml` (WSL). Expected: `SUCCESS`. Agrégalo al CI de `infra/`.
- [ ] **Step 6 [Guía]: Telegram y Healthchecks.**
  - Crea el bot con @BotFather y obtén `TELEGRAM_CHAT_ID`.
  - Crea un *check* en Healthchecks.io con periodo de 5 min y gracia de 10 min, conectado a tu Telegram o correo.
  - `alertmanager.yml` se genera desde la plantilla con el `.env` de `vigia`: `Watchdog` va al webhook de `HEALTHCHECKS_PING_URL` con `repeat_interval: 5m`, y el resto a Telegram.
- [ ] **Step 7: simulacros** (con evidencia en el PR).
  1. Desde `(apps)`: `echo 'homelab_job_ultimo_resultado 0' | curl --data-binary @- http://10.0.20.20:9091/metrics/job/simulacro`. Expected: llega `JobFallo` a Telegram. Después bórralo con `curl -X DELETE …/metrics/job/simulacro`.
  2. `docker compose stop alertmanager` durante 15 min. Expected: Healthchecks.io avisa que el check está *down*. Vuelve a levantarlo y debe volver a *up*.
- [ ] **Step 8:** commit: `infra: vigía con alertas y aviso externo`.

---

### Task 8: Respaldos y prueba de restauración

**Files:**
- Create: `infra/host/volcar-bases.sh`, `infra/host/respaldar-config.sh`, `infra/host/probar-restauracion.sh`, con sus `.service` y `.timer`

**Interfaces:**
- Consumes: el Pushgateway de la Tarea 7 (latidos `respaldo-pg`, `respaldo-config` y `prueba-restauracion`), y los roles de la Tarea 4.
- Produces: archivos en `/mnt/frio/respaldos/{pg,config}/AAAA-MM-DD/` que `metricas-host` mide para `homelab_respaldo_edad_segundos{tipo}`.

- [ ] **Step 1 [Guía] (host): trabajo de vzdump.** En *Datacenter → Backup*: VMs 111, 112 y 120, todos los días a las 01:00, modo `snapshot`, almacenamiento `respaldos` y compresión `zstd`. La retención la pone el almacenamiento. Expected: corre a mano una vez con *Run now* y aparecen los `.vma.zst` en `/mnt/frio/respaldos/dump/`.
- [ ] **Step 2 [Claude Code]: `volcar-bases.sh`.**
  - Para cada esquema listado en `/root/.secretos/esquemas` (formato `base:esquema`, uno por línea), hace `pg_dump -Fc -n <esquema>`.
  - Borra lo que tenga más de 14 días.
  - Sale con un código distinto de 0 si algún volcado falla o pesa 0 bytes.
  - Manda su latido.
  - **Hoy la lista de esquemas está vacía:** el script lo reporta como éxito con 0 esquemas, y los proyectos agregan los suyos al desplegarse.
- [ ] **Step 3 [Claude Code]: `respaldar-config.sh`.** Tar de `/etc/pve`, `/etc/network`, `/etc/exports` y `/etc/fstab`, con 14 días de retención y latido.
- [ ] **Step 4 [Claude Code]: `probar-restauracion.sh`** (mensual, el día 1 a las 03:00).
  - Restaura el último vzdump de `db` como VMID 911, **con la red desconectada** (`qm set 911 --net0 …,link_down=1`).
  - La arranca y confirma con `qm agent 911 ping` y con `qm guest exec 911 -- pg_isready`.
  - Restaura el último `pg_dump` de cada esquema en una base temporal de `db` y compara los conteos de filas por tabla contra el original.
  - Destruye la VM 911 y la base temporal.
  - Manda su latido.
- [ ] **Step 5: verifica** (host): corre `probar-restauracion.sh` a mano. Expected: código 0 y `homelab_job_ultimo_resultado{job="prueba-restauracion"} 1` en Prometheus. **La VM 911 ya no existe al terminar.**
- [ ] **Step 6:** commit: `infra: respaldos y prueba de restauración`.

---

### Task 9: n8n de solo lectura

**Files:**
- Modify: `infra/vigia/compose.yml` (servicio `n8n`)
- Create: `infra/vigia/n8n/resumen-diario.json`, `infra/vigia/n8n/alerta-subagente.json` (flujos exportados, sin credenciales)

- [ ] **Step 1 [Claude Code]: servicio `n8n`** en el compose.
  - Base SQLite en un volumen.
  - `N8N_ENCRYPTION_KEY` desde el `.env`.
  - `NODES_EXCLUDE='["n8n-nodes-base.executeCommand","n8n-nodes-base.ssh"]'`.
  - Publicado solo en `10.0.20.20:5678`; se entra por Tailscale.
  - `mem_limit: 1g`.
- [ ] **Step 2 [Guía]: credenciales en n8n.**
  - Postgres con `lector_vigia`.
  - Las API de Prometheus y Alertmanager (HTTP a la VLAN).
  - Telegram.
  - `ANTHROPIC_API_KEY` para el subagente.
- [ ] **Step 3 [Guía]: flujo "resumen diario"** (07:45).
  - Consulta en Prometheus las alertas activas, los latidos de las últimas 24 h y el uso del frío.
  - Arma un mensaje y lo manda a Telegram.
- [ ] **Step 4 [Guía]: flujo "alerta → subagente"**, disparado por un webhook de Alertmanager (un receptor más, solo para alertas `critical`).
  - Le pasa al modelo la alerta, sus métricas recientes y las últimas filas de las vigilancias.
  - El modelo devuelve un diagnóstico y **una propuesta**.
  - El flujo la manda a Telegram. **No ejecuta nada.**
- [ ] **Step 5: verifica.**
  - Repite el simulacro 1 de la Tarea 7: llegan la alerta y, después, el diagnóstico del subagente.
  - En n8n, un nodo Postgres con `INSERT` usando `lector_vigia` falla con `permission denied`.
  - El nodo "Execute Command" no aparece en el editor.
- [ ] **Step 6:** exporta los flujos sin credenciales y haz commit: `infra: n8n de solo lectura`.

---

### Task 10: Tailscale

- [ ] **Step 1 [Guía] (host):** instala Tailscale desde su repositorio oficial y corre `tailscale up --advertise-routes=10.0.20.0/24`. Aprueba la ruta en la consola de Tailscale.
- [ ] **Step 2: verifica** desde el celular con Tailscale y **fuera del wifi de la casa**: se abren la interfaz de Proxmox (`https://192.168.100.50:8006`) y `http://10.0.20.20:5678` (n8n).
- [ ] **Step 3:** anota en el inventario `acceso_remoto: tailscale` y haz commit: `infra: acceso remoto con Tailscale`.

---

### Task 11: NUT (bloqueada hasta tener el cable USB del UPS)

- [ ] **Step 1 [Tú]:** identifica el modelo exacto del UPS y su puerto de datos: USB-B, USB-A o RJ45 a USB. Consigue el cable.
- [ ] **Step 2 [Guía] (host):**
  - `apt install nut`, en modo `netserver`.
  - En `ups.conf`, el driver que diga la lista de compatibilidad de NUT para tu modelo.
  - En `upsmon.conf`, el apagado ordenado del host (que primero apaga las VMs).
- [ ] **Step 3: verifica.**
  - `upsc <ups>` muestra `ups.status: OL`.
  - Desconecta el UPS de la pared 30 s: `homelab_ups_en_bateria 1` y llega `UpsEnBateria` a Telegram. Reconéctalo.
- [ ] **Step 4:** en el inventario, `ups.monitoreado: true` y el modelo. Commit: `infra: UPS con NUT`.

---

### Task 12: Cierre del tramo 1

**Files:**
- Create: `infra/RESTAURAR-plataforma.md`

- [ ] **Step 1 [Claude Code]: `RESTAURAR-plataforma.md`.** Cómo levantar el mini PC desde cero con este repo:
  - instalar Proxmox;
  - copiar `infra/host/interfaces`;
  - montar el frío por UUID;
  - restaurar las VMs desde `respaldos`;
  - volver a crear los secretos (por nombre).
- [ ] **Step 2: lista de "plataforma lista"** (cada punto con su evidencia en el PR):
  - [ ] `infra-validar` en verde.
  - [ ] Las 3 VMs responden.
  - [ ] Frío montado y con escritura como 2000.
  - [ ] Alertas probadas.
  - [ ] Aviso externo probado.
  - [ ] n8n de solo lectura comprobado.
  - [ ] vzdump y prueba de restauración en verde.
  - [ ] Tailscale funcionando.
  - [ ] NUT funcionando, o anotado como bloqueado.
- [ ] **Step 3:** con esto el proyecto de ingesta puede desplegar su primera pieza: el RESTAURAR de A1.1 en su repo, sobre la VM `apps`.
