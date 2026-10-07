<div align="center">

# 🤝 Dual Agent

**Fais travailler Claude Code et Codex CLI ensemble sur ton projet — chacun sur ce qu'il fait de mieux, avec une mémoire commune et des tests écrits d'avance.**

[![CI](https://github.com/livai225/dual-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/livai225/dual-agent/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-%E2%89%A53.9-blue)
![Dépendances](https://img.shields.io/badge/d%C3%A9pendances-aucune-brightgreen)
![Licence](https://img.shields.io/badge/licence-MIT-lightgrey)
![Statut](https://img.shields.io/badge/statut-b%C3%AAta-orange)

</div>

```bash
dual-agent "ajoute un écran de connexion et l'API d'authentification"
```

Un seul fichier Python, aucune dépendance. Tu décris ce que tu veux ; Dual Agent réécrit la demande en brief précis, la découpe par domaine (UI/UX, backend, tests…), confie chaque morceau à l'agent le plus adapté, fait relire le travail par l'autre, et te rend **une branche Git prête à fusionner**. Ta branche courante n'est jamais touchée.

> ⚠️ **Projet indépendant, non affilié à Anthropic ni à OpenAI.** Il pilote les CLI officielles `claude` (Claude Code) et `codex` (Codex CLI) que tu installes toi-même, avec tes propres comptes.

---

## Sommaire

- [Pourquoi](#pourquoi)
- [Fonctionnalités](#fonctionnalités)
- [Comment ça marche](#comment-ça-marche)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Démarrage rapide](#démarrage-rapide)
- [Utilisation en détail](#utilisation-en-détail)
- [Référence des commandes](#référence-des-commandes)
- [Où sont rangées les données](#où-sont-rangées-les-données)
- [Coût](#coût)
- [Sécurité et limites](#sécurité-et-limites)
- [Statut du projet](#statut-du-projet)
- [Dépannage](#dépannage)
- [Contribuer](#contribuer)
- [Licence](#licence)

---

## Pourquoi

Claude Code et Codex ne sont pas bons aux mêmes choses, et aucun des deux ne relit l'autre. Dual Agent automatise ce que l'on ferait à la main :

1. **Préciser** la demande avant de coder (une demande floue donne un résultat flou) ;
2. **Répartir** le travail : l'agent le plus adapté pour chaque domaine ;
3. **Vérifier** : l'autre agent écrit d'abord les tests, puis relit le résultat ;
4. **Retenir** : les deux agents partagent la même mémoire du projet et s'enrichissent mutuellement ;
5. **Mesurer** : au fil des missions, le choix de l'agent par domaine s'appuie sur des résultats réels et non sur une habitude.

## Fonctionnalités

| | |
|---|---|
| 🧭 **Mode équipe** (par défaut) | Le plan est découpé par domaine ; chaque sous-tâche va à l'agent le plus adapté, relue par l'autre. Si un agent ne produit rien, l'autre prend le relais. |
| ✍️ **Réécriture de la demande** | Ta phrase est transformée en brief structuré (objectif, contraintes, critères de réussite) à partir d'une lecture du projet, puis soumise à ta relecture. |
| 🧪 **Tests d'acceptation écrits d'avance** | L'agent qui n'implémente pas écrit d'abord les tests (fichiers de test uniquement). Ils doivent être **rouges** au départ, et l'implémenteur ne peut pas les modifier : s'il y touche, ils sont restaurés. |
| 📊 **Routage mesuré** | Chaque sous-tâche alimente un journal de résultats par domaine et par agent. Une fois les données suffisantes, l'agent le plus performant est choisi automatiquement. |
| 🧠 **Mémoire partagée** | Conventions, décisions et leçons du projet, injectées dans les prompts des deux agents et exportables vers `CLAUDE.md` / `AGENTS.md`. Rien n'est enregistré sans ta confirmation. |
| 🌿 **Isolation Git** | Tout se passe dans des worktrees dédiés et des branches `dual-agent/<session>/…`. Fusion uniquement quand tu le décides. |
| 🏁 **Mode concours** | `--mode compete` : les deux agents font toute la mission séparément, un intégrateur assemble la meilleure solution. |
| 🔒 **Garde-fous** | Commandes de test proposées par un agent filtrées par liste blanche et exécutées sans shell ; secrets et fichiers générés exclus des commits. |

## Comment ça marche

```
 ta demande
     │
     ▼
 ① Réécriture ──► brief précis (tu relis / modifies)
     │
     ▼
 ② Plan par domaine ──► sous-tâches : ui_ux · frontend · backend · data · tests · …
     │
     ▼   pour chaque sous-tâche
 ┌───────────────────────────────────────────────────────────┐
 │ ③ L'autre agent écrit les tests d'acceptation (rouges)    │
 │ ④ L'agent le plus adapté implémente                       │
 │ ⑤ Tests du projet + tests d'acceptation                   │
 │ ⑥ Relecture par l'autre agent  ──►  OK / À CORRIGER       │
 │ ⑦ Correction forcée si relecture ou tests rouges          │
 └───────────────────────────────────────────────────────────┘
     │
     ▼
 ⑧ Tests finaux (+ relecture globale si plusieurs sous-tâches)
     │
     ▼
 ⑨ Bilan : leçons proposées pour la mémoire partagée (après ta confirmation)
     │
     ▼
 branche  dual-agent/<session>/final   →   dual-agent merge
```

Exemple de répartition par défaut (une **convention** de départ, pas une vérité mesurée — voir [routage mesuré](#routage-mesuré)) :

| Domaine | Agent par défaut |
|---|---|
| `ui_ux`, `frontend`, `docs` | Claude |
| `backend`, `data`, `tests`, `devops`, `security` | Codex |

## Prérequis

- **Python ≥ 3.9**
- **Git**
- **Node.js / npm** — facultatif ; utile seulement pour installer les CLI `claude` et `codex` via `dual-agent setup`, ou si ton projet est en JavaScript
- Un compte pour **Claude Code** et un pour **Codex CLI** (chacun avec ses propres conditions d'utilisation et tarifs)

## Installation

### Option 1 — `pipx` (recommandé)

```bash
pipx install git+https://github.com/livai225/dual-agent.git
```

Avec `pip` simple :

```bash
pip install git+https://github.com/livai225/dual-agent.git
```

### Option 2 — Scripts d'installation

```bash
git clone https://github.com/livai225/dual-agent.git
cd dual-agent
./install.sh            # macOS / Linux  (installe dans ~/.local/bin)
```

```powershell
# Windows (PowerShell)
git clone https://github.com/livai225/dual-agent.git
cd dual-agent
.\install.ps1
```

Si `~/.local/bin` n'est pas dans ton `PATH`, le script t'indique la ligne à ajouter.

### Option 3 — Sans installer

Le projet tient dans un seul fichier :

```bash
python3 dual_agent.py "ta mission"
```

### Connecter Claude et Codex

```bash
dual-agent setup      # installe les CLI manquantes et ouvre les connexions
dual-agent doctor     # vérifie versions, options requises et connexions
```

### Mise à jour / désinstallation

```bash
pipx upgrade dual-agent              # ou : pipx install --force git+https://github.com/livai225/dual-agent.git
pipx uninstall dual-agent

./uninstall.sh [--purge]             # si installé par script (.\uninstall.ps1 sous Windows)
```

> Avant de désinstaller, `dual-agent clean` supprime les worktrees et branches `dual-agent/*` laissés dans tes dépôts. Sans `--purge`, les rapports de missions sont conservés.

## Démarrage rapide

Dans un dépôt Git **propre** (tout est commité) :

```bash
cd mon-projet
dual-agent "ajoute une page de connexion et l'API d'authentification"
```

Dual Agent te montre le brief réécrit, puis le plan avec « qui fait quoi » ; tu valides. À la fin :

```bash
dual-agent list          # sessions du dépôt
dual-agent merge         # fusionne la dernière branche finale dans ta branche
dual-agent clean         # nettoie les worktrees
```

Les rapports (`SUMMARY.md`, revues, tests) se trouvent dans `~/.dual-agent/runs/…`.

## Utilisation en détail

### Réécriture de la demande

Par défaut, ta demande est réécrite en brief précis, puis affichée pour relecture / modification. Pour l'essayer seul, sans lancer d'agent de code :

```bash
dual-agent refine "rends l'appli plus rapide"
```

`--no-refine` envoie ta demande telle quelle ; `--rewriter codex` change l'agent qui la réécrit.

### Équipe et répartition

```bash
dual-agent team                          # qui fait quoi (défaut, mesuré, épinglé)
dual-agent team set ui_ux claude         # forcer un agent pour un domaine
dual-agent team set backend codex --project   # réglage limité à ce projet
dual-agent team set ui_ux auto           # retirer l'épinglage
dual-agent team reset
```

Domaines : `ui_ux`, `frontend`, `backend`, `data`, `tests`, `devops`, `security`, `docs`, `other`. Un réglage manuel l'emporte toujours sur le choix automatique.

### Tests d'acceptation

Avant chaque implémentation, l'autre agent écrit des tests décrivant le résultat attendu. Garanties :

- seuls des **fichiers de test** sont conservés (tout autre fichier produit à ce stade est annulé) ;
- les tests doivent être **rouges** au départ, sinon ils ne prouvent rien et sont signalés ;
- l'implémenteur **ne peut pas les modifier** : toute altération est annulée et indiquée dans le bilan (`rouge→vert (tests restaurés)`) ;
- tests encore rouges après l'implémentation → **correction forcée**.

La commande de test proposée par l'agent doit appartenir à une **liste blanche** (`pytest`, `python -m pytest|unittest`, `npm|pnpm|yarn test`, `composer test`, `go test`, `cargo test`, `npx jest|vitest|mocha`, `phpunit`, `node --test`), sans métacaractères de shell ni options d'exécution de code ; elle est lancée **sans shell**. Désactivation : `--no-accept` (économise un appel par sous-tâche).

### Routage mesuré

Chaque sous-tâche écrit dans `~/.dual-agent/ledger.jsonl` : domaine, agent, a-t-il produit du code, tests d'acceptation passés du premier coup, verdict de relecture, tests finaux, fusion effective. Un score en est tiré.

- Il faut **au moins 3 mesures par agent** dans un domaine, et un **écart d'au moins 0,15**, avant de remplacer la convention par défaut.
- `dual-agent stats` affiche les scores et l'agent retenu par domaine.
- `--calibrate` confie chaque sous-tâche à l'agent **le moins mesuré** du domaine, pour générer des comparaisons.
- `--no-learn` ignore les mesures (réglages manuels et défauts uniquement).

> Les scores sont **indicatifs** : un petit échantillon ou des missions très différentes peuvent les fausser.

### Mémoire partagée

```bash
dual-agent memory                 # afficher
dual-agent memory add "Les composants UI sont dans src/ui, jamais de CSS inline"
dual-agent memory edit
dual-agent memory sync            # écrit un bloc dans CLAUDE.md et AGENTS.md
dual-agent memory reset
```

- La mémoire est propre à chaque projet et injectée (limitée en taille, nettoyée) dans les prompts des deux agents.
- En fin de mission, des leçons sont **proposées** ; rien n'est enregistré sans confirmation (ou `-y`). Sans terminal interactif et sans `-y`, elles sont écrites dans `MEMORY_PROPOSED.md` pour relecture.
- `memory sync` insère un bloc balisé (`<!-- dual-agent:memory:start/end -->`) : le reste de tes fichiers n'est pas touché.
- `--no-memory` désactive tout.

### Options utiles de `run`

```bash
dual-agent "..." --fast               # sans relectures croisées : moins d'appels
dual-agent "..." --test "pytest"      # imposer la commande de test (répétable)
dual-agent "..." --merge              # fusionne la branche finale si les tests passent
dual-agent "..." --mode compete       # les deux agents font toute la mission
dual-agent "..." -y                   # aucune confirmation (voir « Sécurité »)
```

## Référence des commandes

| Commande | Rôle |
|---|---|
| `dual-agent "mission"` | Raccourci de `dual-agent run "mission"` |
| `setup [--relogin]` | Installer et connecter Claude + Codex |
| `status` | État des deux agents |
| `doctor` | Diagnostic complet (versions, options, connexions) |
| `run "mission"` | Lancer une mission |
| `refine "demande"` | Réécrire une demande sans lancer d'agent de code |
| `team [show\|set\|reset]` | Voir ou régler « qui fait quoi » |
| `stats` | Scores mesurés par domaine et par agent |
| `memory [show\|add\|edit\|reset\|sync]` | Mémoire partagée |
| `list` | Sessions du dépôt |
| `merge [--session ID] [-y]` | Fusionner une solution finale |
| `clean [--all] [-y]` | Supprimer worktrees et branches (`--all` : branches finales et rapports aussi) |

<details>
<summary><b>Toutes les options de <code>dual-agent run</code></b></summary>

| Option | Effet |
|---|---|
| `--repo REPO` | Dépôt Git (défaut : dossier courant) |
| `--mode {team,compete}` | `team` (défaut) : chaque sous-tâche à l'agent adapté ; `compete` : les deux font toute la mission |
| `--no-refine` | Ne réécrit pas la demande |
| `--rewriter {claude,codex}` | Agent qui réécrit la demande (défaut : claude) |
| `--fast` | Sans revues croisées |
| `--no-accept` | Sans tests d'acceptation écrits d'avance |
| `--calibrate` | Sous-tâche confiée à l'agent le moins mesuré |
| `--no-learn` | Ignore le routage mesuré |
| `--no-memory` | N'utilise ni ne met à jour la mémoire |
| `--integrator {codex,claude}` | Qui construit la solution finale |
| `--test CMD` / `--no-test` | Commande de test (répétable) / aucun test |
| `--setup CMD` / `--no-setup` | Commande d'installation des dépendances (répétable) / aucune |
| `--merge` | Fusionne la branche finale si les tests passent |
| `--timeout MIN` | Minutes max par appel d'agent (défaut 45) |
| `--keep` | Garde les worktrees après la mission |
| `--allow-dirty` | Continue malgré des modifications non commitées |
| `-y`, `--yes` | Aucune confirmation (brief, plan, mémoire) |

</details>

Variables d'environnement : `DUAL_AGENT_HOME` (dossier de données), `DUAL_AGENT_DEBUG=1` (traceback complet), `NO_COLOR` (sans couleurs).

## Où sont rangées les données

```
~/.dual-agent/
├── runs/<dépôt>/<session>/   worktrees + rapports (reports/SUMMARY.md …)
├── memory/                   mémoire partagée, un fichier par projet
├── ledger.jsonl              journal des résultats (routage mesuré)
├── team.json                 réglages « qui fait quoi » globaux
└── team/                     réglages propres à un projet
```

Dans ton dépôt, Dual Agent ne crée que des **branches** `dual-agent/<session>/{codex,claude,final}` ; aucun fichier n'est ajouté à ta branche tant que tu ne fusionnes pas (sauf `memory sync` si tu le demandes).

## Coût

Chaque appel d'agent consomme de ton quota / crédit. À titre indicatif, **une mission découpée en 3 sous-tâches représente environ 13 appels** (réécriture, plan, 3 × [tests, implémentation, relecture], corrections éventuelles, relecture finale, bilan). Pour réduire : `--fast`, `--no-accept`, `--no-refine`, ou une demande qui ne se découpe pas.

## Sécurité et limites

**Lis ceci avant d'utiliser `-y` ou de lancer l'outil sur un dépôt que tu ne maîtrises pas.**

- **Ce n'est pas un bac à sable.** Les agents tournent avec tes droits, dans des worktrees isolés *côté Git* seulement.
- **Les tests exécutent du code écrit par un agent**, sur ta machine (commande de test du projet, tests d'acceptation). La liste blanche et l'absence de shell réduisent le risque ; elles ne l'annulent pas.
- **Injection de prompt** : un fichier du dépôt (README, commentaire, dépendance…) peut contenir des instructions visant l'agent, qui les transmettrait ensuite à l'autre. Sur un dépôt non fiable, lis le brief et le plan, et **n'utilise pas `-y`**.
- Les secrets courants (`.env`, clés…) sont exclus des commits ; ne compte pas dessus comme unique protection.
- Un score de routage est une mesure **indicative**, pas une garantie de qualité.
- Une relecture par un agent n'est pas une revue humaine : relis la branche finale avant de fusionner.

## Statut du projet

**Bêta.** Soyons précis sur ce qui est vérifié :

- ✅ Tests unitaires et tests de flux complets (réécriture, plan, tests d'acceptation, falsification, relais, mémoire, routage, fusion) passent avec de **faux agents simulés**.
- ✅ La CI exécute les tests unitaires sur Linux, macOS et Windows (Python 3.9 et 3.13) ; les tests de flux tournent sous Linux/macOS uniquement.
- ⚠️ **Non validé de bout en bout avec les vraies CLI** `claude` et `codex` sur toutes les versions, ni sous Windows. Les options des CLI évoluent : `dual-agent doctor` signale les écarts.
- ⚠️ La répartition par défaut est une convention ; seul le routage mesuré (après plusieurs missions) repose sur des données.

Les retours de test sur de vrais projets sont très bienvenus (issues).

## Dépannage

| Symptôme | Piste |
|---|---|
| `Codex — non installé` ou `non connecté` | `dual-agent setup`, puis `dual-agent doctor` |
| « modifications non commitées » | Commite ou `git stash`, ou `--allow-dirty` (à tes risques) |
| Un agent ne produit aucun fichier | L'autre prend le relais ; si aucun n'écrit, la mission s'arrête (code 2) — reformule ou précise la demande |
| Commande de test « refusée » | Elle n'est pas dans la liste blanche : fournis la tienne avec `--test` |
| Une option de CLI n'est plus reconnue | `dual-agent doctor`, puis ouvre une issue avec la version de la CLI concernée |
| Erreur inattendue | `DUAL_AGENT_DEBUG=1 dual-agent …` pour le traceback, puis `dual-agent clean` |
| Mission trop longue | `--timeout`, `--fast`, ou découpe ta demande |

## Contribuer

Les issues et pull requests sont bienvenues.

```bash
git clone https://github.com/livai225/dual-agent.git
cd dual-agent
python -m unittest discover -s tests -v
```

```
dual_agent.py        tout le programme (un seul fichier, stdlib uniquement)
tests/test_core.py   tests unitaires (parseurs, scores, sécurité des commandes, mémoire…)
tests/test_flow.py   missions complètes avec de faux agents (POSIX)
tests/fake_agent.py  faux claude/codex configurables par variables FAKE_*
pyproject.toml       paquet pip/pipx
```

Principes : pas de dépendance externe, Python 3.9 minimum, tout comportement de sécurité accompagné d'un test. Voir le [CHANGELOG](CHANGELOG.md).

## Licence

[MIT](LICENSE). *Claude* et *Claude Code* sont des marques d'Anthropic ; *Codex* et *OpenAI* sont des marques d'OpenAI. Ce projet n'est ni affilié ni approuvé par ces sociétés.
