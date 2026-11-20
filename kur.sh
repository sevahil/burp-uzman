#!/usr/bin/env bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
export LC_ALL=C

KOK="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

hedef_kontrol() {
    case "$(uname -s)" in
        Linux|Darwin) ;;
        *) echo "desteklenmeyen sistem: $(uname -s) (Linux veya macOS gerekir)" >&2; exit 2 ;;
    esac
}

arac_kontrol() {
    local eksik=0
    for arac in python3 git; do
        if ! command -v "$arac" >/dev/null 2>&1; then
            echo "eksik: $arac" >&2
            eksik=1
        fi
    done
    [ "$eksik" -eq 0 ] || exit 3
    python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' \
        || { echo "python3 >= 3.8 gerekli" >&2; exit 3; }
}

dosya_kontrol() {
    local eksik=0
    for f in dogrula.py .gitignore bapps.md kabul-windows.md configs/recipe.md kapsam/recipe.md auth/recipe.md manifest.sha256; do
        if [ ! -f "$KOK/$f" ]; then
            echo "eksik dosya: $f" >&2
            eksik=1
        fi
    done
    [ -d "$KOK/bchecks" ] || { echo "eksik dizin: bchecks" >&2; eksik=1; }
    [ "$eksik" -eq 0 ] || exit 4
}

hedef_kontrol
arac_kontrol
dosya_kontrol

cd "$KOK"
python3 -I -m unittest discover -s tests
python3 -I dogrula.py

echo "kurulum dogrulandi. Sonraki adim: kabul-windows.md (Burp 2026.2.1 uzerinde elle)."
