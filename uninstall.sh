#!/usr/bin/env bash
# Désinstalle Dual Agent. Les rapports de missions (~/.dual-agent/runs) sont conservés
# sauf avec --purge. Les connexions Claude/Codex ne sont pas touchées.
set -euo pipefail

INSTALL_DIR="$HOME/.dual-agent"
BIN_DIR="$HOME/.local/bin"

rm -f "$BIN_DIR/dual-agent" "$INSTALL_DIR/dual_agent.py" "$INSTALL_DIR/dual_agent_cli.py" "$INSTALL_DIR/orchestrator.py"

if [ "${1:-}" = "--purge" ]; then
  rm -rf "$INSTALL_DIR"
  echo "Dual Agent supprimé, rapports compris."
else
  echo "Dual Agent supprimé. Rapports conservés dans $INSTALL_DIR/runs (relance avec --purge pour les effacer)."
fi
echo "Les branches dual-agent/* de tes dépôts restent : utilise 'dual-agent clean' avant de désinstaller si besoin."
