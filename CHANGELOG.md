# Changelog

## 1.4.1
- `ask` : les avertissements de la CLI Claude (stderr) ne polluent plus la réponse ; consigne anti-remarques hors sujet ; rendu terminal soigné (titres, gras, code, puces) ; titres traduits dans la langue de la question.
- `dual-agent "question"` lancé **hors dépôt Git** devient automatiquement une analyse en lecture seule (au lieu d'une erreur).
- `ask` fonctionne avec un seul agent si l'autre n'est pas installé.

## 1.4.0
- **`dual-agent ask "..."`** : analyse en lecture seule, **sans dépôt Git** (ex. « pourquoi le serveur est lent ? »). Les deux agents enquêtent en parallèle, puis une synthèse recoupe les deux rapports (accords, désaccords, causes probables, actions recommandées non exécutées). `--agent claude|codex` pour un seul agent, `--dir` pour choisir le dossier.
- Lecture seule garantie par les outils : Claude sans Edit/Write et avec une liste blanche de commandes de diagnostic ; Codex en sandbox `read-only`.
- `dual-agent` seul, hors dépôt Git, propose maintenant ce mode d'analyse.

## 1.3.0
- **Tests d'acceptation** : pour chaque sous-tâche, l'agent qui n'implémente pas écrit d'abord les tests (fichiers de test uniquement), vérifiés rouges avant l'implémentation ; l'implémenteur ne peut pas les modifier ; tests rouges = correction forcée.
- **Routage mesuré** : journal des résultats par domaine et par agent, score, décision automatique (≥ 3 mesures par agent, écart ≥ 0,15), `--calibrate`, `--no-learn`, `dual-agent stats`, `dual-agent team set <domaine> auto`.
- Liste blanche stricte pour les commandes de test proposées par un agent.
- Correctif : identifiant de session aléatoire (deux lancements la même seconde se télescopaient).
- Correctif : fichiers générés par les tests (`__pycache__`, `.pytest_cache`…) exclus des commits.
- Erreurs imprévues affichées proprement (`DUAL_AGENT_DEBUG=1` pour le traceback), `| head` ne casse plus la sortie.
- Installation par `pip`/`pipx` (`pyproject.toml`), suite de tests et CI.

## 1.2.0
- **Mode équipe** (défaut) : plan par domaine, chaque sous-tâche confiée à l'agent le plus adapté, relecture croisée, correction, relais si un agent ne produit rien.
- **Mémoire partagée** par projet, injectée dans les prompts, enrichie en fin de mission après confirmation ; `dual-agent memory`, `memory sync` vers `CLAUDE.md` / `AGENTS.md`.
- `dual-agent team` pour voir et régler « qui fait quoi ».
- Mode concours conservé : `--mode compete`.

## 1.1.0
- **Réécriture de la demande** en brief précis (lecture seule du projet), relecture / édition avant lancement, `dual-agent refine`.

## 1.0.0
- Réécriture complète en un seul fichier Python sans dépendance.
- Prompts via stdin (plus de limite de ligne de commande), exécutables résolus avec chemin complet, dépendances installées dans les worktrees, timeouts qui tuent les processus enfants, commits sans signature GPG ni hooks et sans secrets.
- Commandes `merge`, `clean`, `list`, `doctor`.

## 0.3.0
- Première version : worktrees isolés, revue croisée, intégrateur final.
