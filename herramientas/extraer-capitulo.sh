#!/usr/bin/env bash
# Extrae un rango de páginas de un PDF de la biblioteca local a texto plano.
# La salida queda en biblioteca/.extraido/, que está en .gitignore: nunca entra a Git.
#
# Uso: extraer-capitulo.sh <pdf> <pagina_inicio> <pagina_fin> <nombre_salida>
set -euo pipefail

uso() {
  echo "Uso: $(basename "$0") <pdf> <pagina_inicio> <pagina_fin> <nombre_salida>" >&2
  exit 2
}

[[ $# -eq 4 ]] || uso

pdf=$1
inicio=$2
fin=$3
nombre=$4

if ! command -v pdftotext >/dev/null 2>&1; then
  echo "Error: falta pdftotext (paquete poppler-utils)." >&2
  exit 1
fi

[[ -f $pdf ]] || { echo "Error: no existe el PDF '$pdf'." >&2; exit 1; }
[[ $inicio =~ ^[1-9][0-9]*$ && $fin =~ ^[1-9][0-9]*$ ]] \
  || { echo "Error: las páginas deben ser enteros positivos." >&2; exit 1; }
(( inicio <= fin )) || { echo "Error: pagina_inicio ($inicio) es mayor que pagina_fin ($fin)." >&2; exit 1; }
[[ $nombre != */* ]] || { echo "Error: nombre_salida no debe contener '/'." >&2; exit 1; }

# La biblioteca vive en la raíz del repo, un nivel arriba de herramientas/.
raiz=$(cd "$(dirname "$0")/.." && pwd)
destino="$raiz/biblioteca/.extraido"
mkdir -p "$destino"

salida="$destino/$nombre.txt"
pdftotext -layout -f "$inicio" -l "$fin" "$pdf" "$salida"
echo "$salida"
