#!/usr/bin/env bash
# Installe Dual Agent pour l'utilisateur courant (macOS / Linux).
# Usage : ./install.sh [--no-setup]
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/.dual-agent"
BIN_DIR="$HOME/.local/bin"

PY=""
for cand in python3 python; do
  if command -v "$cand" >/dev/null 2>&1 && \
     "$cand" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' 2>/dev/null; then
    PY="$(command -v "$cand")"
    break
  fi
done
if [ -z "$PY" ]; then
  echo "Python 3.9+ est requis (aucune version compatible trouvée)." >&2
  exit 1
fi
command -v git >/dev/null 2>&1 || { echo "Git est requis." >&2; exit 1; }

mkdir -p "$INSTALL_DIR" "$BIN_DIR"
cp "$HERE/dual_agent.py" "$INSTALL_DIR/dual_agent.py"
# Nettoyage des fichiers des anciennes versions (0.x)
rm -f "$INSTALL_DIR/dual_agent_cli.py" "$INSTALL_DIR/orchestrator.py"

cat > "$BIN_DIR/dual-agent" <<EOF
#!/usr/bin/env bash
exec "$PY" "\$HOME/.dual-agent/dual_agent.py" "\$@"
EOF
chmod +x "$BIN_DIR/dual-agent"

echo "Dual Agent installé : $BIN_DIR/dual-agent"
case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *)
    echo
    echo "Ajoute ce dossier à ton PATH (puis rouvre le terminal) :"
    echo "  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc   # ou ~/.zshrc"
    ;;
esac

if [ "${1:-}" != "--no-setup" ]; then
  echo
  "$BIN_DIR/dual-agent" setup
else
  echo "Lance ensuite : dual-agent setup"
fi
