"""Tests de flux : de vraies missions Dual Agent avec de faux `claude` / `codex` (tests/fake_agent.py)."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FAKE = Path(__file__).resolve().parent / "fake_agent.py"
DUAL = ROOT / "dual_agent.py"


@unittest.skipIf(os.name == "nt", "les faux agents sont des scripts POSIX")
@unittest.skipUnless(shutil.which("git"), "git requis")
class FlowTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        for name in ("claude", "codex"):
            shim = self.bin / name
            shim.write_text(f'#!/bin/sh\nFAKE_NAME={name} exec "{sys.executable}" "{FAKE}" "$@"\n')
            shim.chmod(0o755)
        self.home = self.tmp / "home"
        self.log = self.tmp / "log"
        self.log.mkdir()
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        self.git("init", "-q")
        self.git("symbolic-ref", "HEAD", "refs/heads/main")
        (self.repo / "package.json").write_text('{"scripts":{"test":"echo ok"}}')
        self.git("add", "-A")
        self.git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init")

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, capture_output=True, text=True, check=True).stdout.strip()

    def run_dual(self, *args, **env):
        e = dict(os.environ, PATH=f"{self.bin}{os.pathsep}{os.environ['PATH']}", DUAL_AGENT_HOME=str(self.home),
                 FAKE_LOG=str(self.log), NO_COLOR="1", **env)
        return subprocess.run([sys.executable, str(DUAL), *args], cwd=self.repo, env=e, capture_output=True,
                              text=True, timeout=120)

    def mission(self, *extra, task="corrige le paiement", **env):
        return self.run_dual(task, "--no-setup", "--no-refine", "-y", *extra, **env)

    def calls(self):
        p = self.log / "calls.log"
        if not p.exists():
            return []
        return [tuple(line.split("\t")[:3]) for line in p.read_text().splitlines()]

    def summary(self):
        found = sorted(self.home.glob("runs/*/*/reports/SUMMARY.md"))
        return found[-1].read_text(encoding="utf-8") if found else ""

    def final_branches(self):
        return self.git("branch", "--list", "dual-agent/*/final")

    def test_team_mission_routes_by_domain_and_learns(self):
        r = self.mission()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        calls = self.calls()
        self.assertIn(("claude", "impl", "s1"), calls)     # ui_ux → Claude
        self.assertIn(("codex", "impl", "s2"), calls)      # backend → Codex
        self.assertIn(("codex", "spec", "s1"), calls)      # tests écrits par l'autre agent
        self.assertIn(("claude", "spec", "s2"), calls)
        self.assertTrue(self.final_branches())
        self.assertIn("vert→vert", self.summary())         # tableau d'acceptation présent
        self.assertTrue(list(self.home.glob("memory/*.md")))
        self.assertTrue((self.home / "ledger.jsonl").exists())
        self.assertEqual(self.git("branch", "--show-current"), "main")  # ta branche n'a pas bougé

    def test_failing_acceptance_forces_a_fix_and_blocks_tampering(self):
        r = self.mission(FAKE_PLAN="single", FAKE_IMPL_JUNK="claude", FAKE_IMPL_TAMPER="1")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("modifications annulées", r.stdout)
        self.assertIn(("claude", "fix", "s1"), self.calls())
        self.assertIn("rouge→vert (tests restaurés)", self.summary())

    def test_agent_that_produces_nothing_is_replaced(self):
        r = self.mission("--no-learn", FAKE_PLAN="single", FAKE_NOWRITE="claude")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("prend le relais", r.stdout)
        self.assertIn(("codex", "impl", "s1"), self.calls())

    def test_agent_proposed_shell_command_is_never_executed(self):
        r = self.mission(FAKE_PLAN="single", FAKE_SPEC_CMD="pytest; touch pwned.txt")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("refusée", r.stdout)
        self.assertEqual(list(self.tmp.rglob("pwned.txt")), [])

    def test_test_author_cannot_write_production_code(self):
        r = self.mission(FAKE_PLAN="single", FAKE_SPEC_PROD="1")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("hors tests", r.stdout)
        branch = self.final_branches().split()[-1]
        self.assertNotIn("prod_code.py", self.git("ls-tree", "-r", "--name-only", branch))

    def test_memory_is_not_saved_without_confirmation(self):
        r = self.run_dual("une mission", "--no-setup", "--no-refine")  # pas de -y, pas de terminal
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Non enregistré", r.stdout)
        self.assertFalse(list(self.home.glob("memory/*.md")))

    def test_compete_mode_still_works(self):
        r = self.mission("--mode", "compete")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Mission terminée", r.stdout)

    def test_no_agent_output_is_an_error(self):
        r = self.mission(FAKE_PLAN="single", FAKE_NOWRITE="claude,codex")
        self.assertEqual(r.returncode, 2)
        self.assertIn("aucun", r.stdout.lower())

    def test_dirty_repository_is_refused(self):
        (self.repo / "new.txt").write_text("x")
        r = self.mission()
        self.assertEqual(r.returncode, 2)
        self.assertIn("modifications non commitées", r.stdout)

    def test_merge_command_and_stats(self):
        self.assertEqual(self.mission(FAKE_PLAN="single").returncode, 0)
        r = self.run_dual("merge", "-y")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn('"merged"', (self.home / "ledger.jsonl").read_text(encoding="utf-8"))
        r = self.run_dual("stats")
        self.assertEqual(r.returncode, 0)
        self.assertIn("ui_ux", r.stdout)

    # -- mode `ask` : analyse en lecture seule, hors dépôt Git ---------------------------------
    def ask(self, *args, **env):
        plain = self.tmp / "plain"                      # dossier qui n'est PAS un dépôt Git
        plain.mkdir(exist_ok=True)
        e = dict(os.environ, PATH=f"{self.bin}{os.pathsep}{os.environ['PATH']}", DUAL_AGENT_HOME=str(self.home),
                 FAKE_LOG=str(self.log), NO_COLOR="1", **env)
        return subprocess.run([sys.executable, str(DUAL), "ask", *args], cwd=plain, env=e,
                              capture_output=True, text=True, timeout=120), plain

    def test_ask_two_agents_then_synthesis_without_git(self):
        r, plain = self.ask("pourquoi le serveur est lent ?")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        calls = self.calls()
        self.assertIn(("claude", "diag", "-"), calls)
        self.assertIn(("codex", "diag", "-"), calls)
        self.assertIn(("claude", "synth", "-"), calls)
        self.assertIn("Synthèse simulée", r.stdout)
        self.assertIn("both", r.stdout)                  # la synthèse a reçu les deux rapports
        self.assertTrue(list(self.home.glob("ask/*/SYNTHESE.md")))
        self.assertEqual(list(plain.iterdir()), [])      # rien n'est écrit dans le dossier analysé

    def test_ask_single_agent_has_no_synthesis(self):
        r, _ = self.ask("analyse", "--agent", "codex")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual([c for c in self.calls() if c[1] == "synth"], [])
        self.assertEqual([c[0] for c in self.calls() if c[1] == "diag"], ["codex"])

    def test_ask_survives_one_failing_agent(self):
        r, _ = self.ask("analyse", FAKE_DIAG_FAIL="codex")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Un seul rapport", r.stdout)
        self.assertEqual([c for c in self.calls() if c[1] == "synth"], [])

    def test_ask_cli_warnings_on_stderr_do_not_pollute_the_answer(self):
        r, _ = self.ask("analyse", FAKE_STDERR_NOISE="1")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("Permission allow rule", r.stdout)
        self.assertNotIn("Permission allow rule", "".join(p.read_text() for p in self.home.glob("ask/*/*.md")))

    def test_plain_request_outside_git_becomes_a_read_only_analysis(self):
        plain = self.tmp / "plain2"
        plain.mkdir()
        e = dict(os.environ, PATH=f"{self.bin}{os.pathsep}{os.environ['PATH']}", DUAL_AGENT_HOME=str(self.home),
                 FAKE_LOG=str(self.log), NO_COLOR="1")
        r = subprocess.run([sys.executable, str(DUAL), "analyse le serveur"], cwd=plain, env=e,
                           capture_output=True, text=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("lecture seule", r.stdout)
        self.assertIn(("claude", "synth", "-"), self.calls())

    def test_ask_all_agents_failing_is_an_error(self):
        r, _ = self.ask("analyse", FAKE_DIAG_FAIL="claude,codex")
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
