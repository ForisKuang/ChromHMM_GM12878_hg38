#!/usr/bin/env bash
set -euo pipefail

CELL="GM12878"
ASSEMBLY="GRCh38"

MARKS=(
  "H3K27ac"
  "H3K4me3"
  "H3K4me1"
  "H3K36me3"
  "H3K27me3"
  "H3K9me3"
)

OUTDIR="bams_${CELL}_${ASSEMBLY}_all6"
TABLE="cellmarkfiletable.txt"

mkdir -p "$OUTDIR"
: > "$TABLE"

for MARK in "${MARKS[@]}"; do
  echo "=== ${MARK} ==="

  URL="https://www.encodeproject.org/search/?type=File&file_format=bam&assay_title=Histone+ChIP-seq&assembly=${ASSEMBLY}&status=released&biosample_ontology.term_name=${CELL}&target.label=${MARK}&format=json&limit=all"

  JSON=$(curl -sL "$URL")
  N=$(echo "$JSON" | jq '.["@graph"] | length')

  if [[ "$N" -eq 0 ]]; then
    echo "  ❌ None found"
    continue
  fi

  echo "$JSON" | jq -r '.["@graph"][] | .accession + "\t" + .href' | \
  while IFS=$'\t' read -r ACC HREF; do
    [[ -z "$HREF" || "$HREF" == "null" ]] && continue

    DEST="${OUTDIR}/${ACC}.bam"
    echo "  ✅ ${ACC}"

    curl -sL "https://www.encodeproject.org${HREF}" -o "$DEST"
    echo -e "${CELL}\t${MARK}\t${ACC}.bam" >> "$TABLE"
  done

  echo
done

echo "Done."

