#!/usr/bin/env bash
set -eo pipefail   # <- removed -u to avoid unbound var crashes

CELL="K562"
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
TABLE="cellmarkfiletable_${CELL}.txt"

mkdir -p "$OUTDIR"
: > "$TABLE"

echo "Downloading BAMs for ${CELL} (${ASSEMBLY}) into ${OUTDIR}"
echo "Writing ChromHMM table to ${TABLE}"
echo

for MARK in "${MARKS[@]}"; do
  echo "=== Mark: ${MARK} ==="

  ACCS=$(python3 - <<PY
import json, urllib.parse, urllib.request

assembly = "${ASSEMBLY}"
mark = "${MARK}"

url = (
  "https://www.encodeproject.org/search/?"
  "type=File"
  "&assembly=" + assembly +
  "&status=released"
  "&file_type=bam"
  "&output_type=alignments"
  "&biosample_ontology.term_name=K562"
  "&assay_title=Histone+ChIP-seq"
  "&target.label=" + mark +
  "&format=json&limit=all"
)

req = urllib.request.Request(url, headers={"Accept": "application/json"})
with urllib.request.urlopen(req) as resp:
    j = json.load(resp)

for f in j.get("@graph", []):
    if f.get("assembly") == assembly and f.get("file_format") == "bam":
        acc = f.get("accession")
        if acc:
            print(acc)
PY
)

  if [[ -z "$ACCS" ]]; then
    echo "  No BAM files found"
    echo
    continue
  fi

  while read -r ACC; do
    URL="https://www.encodeproject.org/files/${ACC}/@@download/${ACC}.bam"
    BAM="${OUTDIR}/${ACC}.bam"

    if [[ ! -f "$BAM" ]]; then
      echo "  Downloading ${ACC}"
      curl -sSL "$URL" -o "$BAM"
    else
      echo "  Already have ${ACC}"
    fi

    ABSPATH="$(cd "${OUTDIR}" && pwd)/${ACC}.bam"
    printf "%s\t%s\t%s\n" "$CELL" "$MARK" "$ABSPATH" >> "$TABLE"

  done <<< "$ACCS"

  echo
done

echo "Done."
echo "BAMs in:   ${OUTDIR}"
echo "Filetable: ${TABLE}"

