"""Faux `claude` / `codex` pour les tests de flux : répond au protocole de Dual Agent sans appeler de modèle.

Le nom de l'agent vient de FAKE_NAME ; le journal des appels est écrit dans $FAKE_LOG/calls.log.
Variables de scénario : FAKE_PLAN (single | single_backend), FAKE_BAD_PLAN, FAKE_FIX, FAKE_NOWRITE (noms séparés
par des virgules), FAKE_IMPL_JUNK, FAKE_IMPL_TAMPER, FAKE_SPEC_NONE, FAKE_SPEC_GREEN, FAKE_SPEC_PROD, FAKE_SPEC_CMD, FAKE_DIAG_FAIL.
"""
import json, os, re, sys, time

name = os.environ["FAKE_NAME"]
args = sys.argv[1:]
if args[:2] in (["auth", "status"], ["login", "status"]):
    print("logged in"); sys.exit(0)
if "--version" in args:
    print(f"{name} 0.0-fake"); sys.exit(0)
if "--help" in args:
    print("--allowedTools --permission-mode --disallowedTools --sandbox --output-last-message"); sys.exit(0)

prompt = sys.stdin.read()
write = ("acceptEdits" in args) or ("workspace-write" in args)
last = args[args.index("-o") + 1] if "-o" in args else None
log_dir = os.environ.get("FAKE_LOG", "/tmp")

m = re.search(r"SUBTASK — (s\d)|subtask (s\d)", prompt)
st = next((g for g in m.groups() if g), "-") if m else "-"
kind = ("diag" if "READ-ONLY DIAGNOSTIC" in prompt else
        "synth" if "synthesising two independent" in prompt else
        "refine" if "tech lead preparing a work order" in prompt else
        "plan" if "splitting a brief into subtasks" in prompt else
        "retro" if "shared project memory that two AI developers" in prompt else
        "spec" if "writing acceptance tests BEFORE implementation" in prompt else
        "review" if "reviewing" in prompt and "VERDICT" in prompt else
        "fix" if "Blocking issues were found in your work" in prompt else
        "impl" if write else "other")
with open(os.path.join(log_dir, "calls.log"), "a") as f:
    f.write(f"{name}\t{kind}\t{st}\tmemory={'<project_memory>' in prompt}\tacc={'ACCEPTANCE TESTS (written' in prompt}\n")

def reply(text):
    print(text)
    if last:
        open(last, "w").write(text)
    sys.exit(0)

if kind == "diag":
    if name in os.environ.get("FAKE_DIAG_FAIL", "").split(","):
        print("boom"); sys.exit(1)
    reply(f"## Summary\n{name}: le disque est saturé par les logs (rapport simulé pour les tests).\n## Findings\n- df: 98%")
if kind == "synth":
    reply("## Answer\nSynthèse simulée : disque saturé.\n## What both agree on\n- df 98%\n" + ("both" if "REPORT FROM CLAUDE" in prompt and "REPORT FROM CODEX" in prompt else "one"))
if kind == "refine":
    reply("<brief>\n## Demande d'origine\nX\n## Objectif\n" + "Brief precis genere avec contexte verifie et criteres. " * 3 + "\n</brief>")
if kind == "plan":
    if os.environ.get("FAKE_BAD_PLAN"):
        reply("pas de json ici")
    subs = [
        {"title": "Écran de paiement", "domain": "ui_ux", "description": "Construire l'écran de paiement."},
        {"title": "Callback API", "domain": "backend", "description": "Corriger le callback de paiement côté API."},
    ]
    if os.environ.get("FAKE_PLAN") == "single":
        subs = subs[:1]
    if os.environ.get("FAKE_PLAN") == "single_backend":
        subs = subs[1:]
    reply("<plan>" + json.dumps({"subtasks": subs}) + "</plan>")
if kind == "retro":
    reply("<memory>\n- claude→codex: les composants UI vivent dans src/components\n- Les tests se lancent avec npm test\n</memory>")
if kind == "spec":
    if os.environ.get("FAKE_SPEC_NONE"):
        reply("Pas de tests automatisables ici.\n<acceptance>\ncommand:\n</acceptance>")
    os.makedirs("tests", exist_ok=True)
    body = "self.assertTrue(True)" if os.environ.get("FAKE_SPEC_GREEN") else f"self.assertTrue(glob.glob('*_{st}_*_*.txt'), 'not implemented')"
    open(f"tests/test_accept_{st}.py", "w").write(
        f"import glob, unittest\nclass T(unittest.TestCase):\n    def test_done(self):\n        {body}\n")
    if os.environ.get("FAKE_SPEC_PROD"):
        open("prod_code.py", "w").write("print('prod')\n")
    cmd = os.environ.get("FAKE_SPEC_CMD") or f"python3 -m unittest tests/test_accept_{st}.py"
    reply(f"Tests écrits.\n<acceptance>\ncommand: {cmd}\n</acceptance>")
if kind == "review":
    flag = os.path.join(log_dir, "fix_done")
    if os.environ.get("FAKE_FIX") and st == "s1" and not os.path.exists(flag):
        open(flag, "w").write("1")
        reply("## Blocking\n- bug réel\nLESSON: utiliser le helper formatMoney\nVERDICT: FIX")
    reply("## Good decisions\nok\nLESSON: utiliser le helper formatMoney\nVERDICT: OK")
if kind in ("impl", "fix"):
    if name in os.environ.get("FAKE_NOWRITE", "").split(",") and kind == "impl":
        reply(f"{name} n'a rien fait")
    if kind == "impl" and os.environ.get("FAKE_IMPL_JUNK") == name:
        open(f"junk_{name}_{time.time_ns()}.txt", "w").write("junk\n")   # change, mais ne satisfait pas le test
    else:
        open(f"{name}_{st}_{kind}_{time.time_ns()}.txt", "w").write(f"work by {name}\n")
    if kind == "impl" and os.environ.get("FAKE_IMPL_TAMPER"):
        p = f"tests/test_accept_{st}.py"
        if os.path.exists(p):
            open(p, "w").write("import unittest\nclass T(unittest.TestCase):\n    def test_done(self):\n        self.assertTrue(True)\n")
    reply(f"{name} done {st} {kind}")
reply(f"## Verdict\n{name} review: looks fine")
