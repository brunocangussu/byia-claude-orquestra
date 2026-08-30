#!/usr/bin/env python3
"""Testes do auditor offline de remoção."""

from __future__ import annotations

import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("audit-removal.py")
SCHEMA = Path(__file__).parents[1] / "schemas" / "audit-ledger-v1.json"


class AuditRemovalTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="orq-audit-removal-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "Projeto ç com espaço"
        self.root.mkdir()
        self.ledger = self.root / "memory" / "audits" / "legacy-billing.json"
        files = {
            "src/index.ts": "import { legacyBilling } from './billing';\nexport { legacyBilling };\n",
            "src/service.ts": "const adapter = legacy_billing;\nconst queue = LEGACY_BILLING;\n",
            "src/ui.tsx": "render(<LegacyBilling />);\nfetch('/legacy-billing');\n",
            "src/worker.ts": "runLegacyBilling();\nconst key = 'legacy billing';\n",
            "tests/service.test.ts": "describe('legacyBilling', () => {});\n",
            "infra/main.tf": "name = \"legacy-billing\"\n",
            "scripts/migrate.py": "TABLE = 'legacy_billing'\n",
            "docs/current.md": "Remove LegacyBilling after migration.\n",
            "docs/history.md": "Historical record: legacy-billing was retired.\n",
        }
        for relative, content in files.items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            text=True,
            capture_output=True,
            timeout=10,
        )

    def scan(self, target: str = "legacy billing") -> subprocess.CompletedProcess[str]:
        return self.run_cli(
            "scan",
            "--root",
            str(self.root),
            "--target",
            target,
            "--ledger",
            str(self.ledger),
            "--retain",
            "docs/history.md",
            "--critical",
            "src/index.ts",
            "--require",
            "unit",
            "--graph-receipt",
            "search_graph=legacy billing",
        )

    def verify(self, *extra: str, target: str = "legacy billing") -> subprocess.CompletedProcess[str]:
        return self.run_cli(
            "verify",
            "--ledger",
            str(self.ledger),
            "--root",
            str(self.root),
            "--target",
            target,
            "--retain",
            "docs/history.md",
            "--critical",
            "src/index.ts",
            "--require",
            "unit",
            *extra,
        )

    def test_scan_finds_thirteen_anchors_and_does_not_scan_its_ledger(self) -> None:
        first = self.scan()
        self.assertEqual(first.returncode, 1, first.stderr)
        payload = json.loads(first.stdout)
        self.assertEqual(payload["status"], "needs-removal")
        ledger = json.loads(self.ledger.read_text(encoding="utf-8"))
        self.assertEqual(len(ledger["evidence"]), 13)
        retained = [item for item in ledger["evidence"] if item["status"] == "retained-historical"]
        self.assertEqual(len(retained), 1)
        self.assertEqual(retained[0]["path"], "docs/history.md")
        self.assertEqual(ledger["graphReceipts"][0]["tool"], "search_graph")
        self.assertEqual(ledger["graphReceipts"][0]["query"], "legacy billing")

        second = self.scan()
        self.assertEqual(second.returncode, 1, second.stderr)
        rescanned = json.loads(self.ledger.read_text(encoding="utf-8"))
        self.assertEqual(len(rescanned["evidence"]), 13, "o ledger não pode se autocontaminar")
        self.assertFalse(any(item["path"].startswith("memory/audits/") for item in rescanned["evidence"]))

    def test_incomplete_removal_fails_and_complete_removal_with_receipt_passes(self) -> None:
        self.assertEqual(self.scan().returncode, 1)
        for path in self.root.rglob("*"):
            if path.is_file() and path != self.ledger and path.as_posix().endswith("docs/history.md") is False:
                path.write_text("target removed\n", encoding="utf-8")
        (self.root / "src/index.ts").write_text("export const billing = true;\n", encoding="utf-8")
        (self.root / "src/service.ts").write_text("const legacyBilling = true;\n", encoding="utf-8")

        incomplete = self.verify("--receipt", "unit=pass")
        self.assertEqual(incomplete.returncode, 1, incomplete.stderr)
        self.assertEqual(json.loads(incomplete.stdout)["status"], "fail")

        (self.root / "src/service.ts").write_text("const billing = true;\n", encoding="utf-8")
        complete = self.verify("--receipt", "unit=pass")
        self.assertEqual(complete.returncode, 0, complete.stderr)
        self.assertEqual(json.loads(complete.stdout)["status"], "pass")
        final = json.loads(self.ledger.read_text(encoding="utf-8"))
        self.assertEqual(final["verification"]["status"], "pass")
        self.assertTrue(any(item["status"] == "removed" for item in final["evidence"]))
        self.assertTrue(any(item["status"] == "retained-historical" for item in final["evidence"]))

        repeated = self.verify("--receipt", "unit=pass")
        self.assertEqual(repeated.returncode, 0, repeated.stderr)
        repeated_ledger = json.loads(self.ledger.read_text(encoding="utf-8"))
        self.assertTrue(any(item["status"] == "removed" for item in repeated_ledger["evidence"]))

    def test_missing_receipt_or_critical_anchor_fails(self) -> None:
        self.assertEqual(self.scan().returncode, 1)
        missing_receipt = self.verify()
        self.assertEqual(missing_receipt.returncode, 1)
        self.assertIn("unit", json.loads(missing_receipt.stdout)["missingReceipts"])

        (self.root / "src/index.ts").unlink()
        missing_anchor = self.verify("--receipt", "unit=pass")
        self.assertEqual(missing_anchor.returncode, 1)
        self.assertIn("src/index.ts", json.loads(missing_anchor.stdout)["missingCriticalAnchors"])

    def test_target_is_data_not_shell_and_unicode_paths_work(self) -> None:
        marker = self.root / "PWNED"
        target = f"$(touch {marker})"
        source = self.root / "src" / "ameaça.txt"
        source.write_text(target + "\n", encoding="utf-8")
        result = self.scan(target)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertFalse(marker.exists())
        ledger = json.loads(self.ledger.read_text(encoding="utf-8"))
        self.assertEqual(ledger["evidence"][0]["path"], "src/ameaça.txt")

    def test_invalid_ledger_returns_schema_error_exit_two(self) -> None:
        self.ledger.parent.mkdir(parents=True, exist_ok=True)
        self.ledger.write_text("not-json", encoding="utf-8")
        result = self.verify()
        self.assertEqual(result.returncode, 2)
        self.assertIn("INVALID_LEDGER", result.stderr)

    def test_verify_rejects_tampered_scope_in_ledger(self) -> None:
        self.assertEqual(self.scan().returncode, 1)
        payload = json.loads(self.ledger.read_text(encoding="utf-8"))
        payload["exclusions"] = ["*"]
        self.ledger.write_text(json.dumps(payload), encoding="utf-8")
        result = self.verify("--receipt", "unit=pass")
        self.assertEqual(result.returncode, 2)
        self.assertIn("SCOPE_MISMATCH", result.stderr)

    def test_malformed_ledger_types_return_exit_two_without_traceback(self) -> None:
        self.assertEqual(self.scan().returncode, 1)
        payload = json.loads(self.ledger.read_text(encoding="utf-8"))
        payload["target"] = "legacy billing"
        self.ledger.write_text(json.dumps(payload), encoding="utf-8")
        result = self.verify()
        self.assertEqual(result.returncode, 2)
        self.assertIn("INVALID_LEDGER", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_nested_dependency_directories_are_excluded(self) -> None:
        nested = self.root / "packages" / "web" / "node_modules" / "package.js"
        nested.parent.mkdir(parents=True)
        nested.write_text("legacyBilling\n", encoding="utf-8")
        result = self.scan()
        self.assertEqual(result.returncode, 1)
        payload = json.loads(self.ledger.read_text(encoding="utf-8"))
        self.assertFalse(any("node_modules" in item["path"] for item in payload["evidence"]))

    def test_non_utf8_target_is_ambiguous_instead_of_silently_skipped(self) -> None:
        binary = self.root / "assets" / "blob.bin"
        binary.parent.mkdir()
        binary.write_bytes(b"\x00legacyBilling\xff")
        self.scan()
        payload = json.loads(self.ledger.read_text(encoding="utf-8"))
        matches = [item for item in payload["evidence"] if item["path"] == "assets/blob.bin"]
        self.assertEqual(matches[0]["status"], "ambiguous")

    def test_critical_anchor_cannot_escape_root(self) -> None:
        for critical in ("../../outside", "/etc/passwd", "C:/Windows/System32"):
            with self.subTest(critical=critical):
                result = self.run_cli(
                    "scan", "--root", str(self.root), "--target", "legacy billing",
                    "--ledger", str(self.ledger), "--critical", critical,
                )
                self.assertEqual(result.returncode, 2)
                self.assertIn("critical", result.stderr.lower())

    def test_dot_relative_critical_anchor_is_idempotent(self) -> None:
        scan = self.run_cli(
            "scan",
            "--root",
            str(self.root),
            "--target",
            "alvo ausente",
            "--ledger",
            str(self.ledger),
            "--critical",
            "./src/index.ts",
        )
        self.assertEqual(scan.returncode, 0, scan.stderr)
        args = (
            "verify",
            "--ledger",
            str(self.ledger),
            "--root",
            str(self.root),
            "--target",
            "alvo ausente",
            "--critical",
            "./src/index.ts",
        )
        first = self.run_cli(*args)
        second = self.run_cli(*args)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)

    def test_matching_is_case_insensitive(self) -> None:
        upper = self.root / "docs" / "upper.md"
        upper.write_text("LEGACY BILLING\n", encoding="utf-8")
        self.scan()
        payload = json.loads(self.ledger.read_text(encoding="utf-8"))
        self.assertTrue(any(item["path"] == "docs/upper.md" for item in payload["evidence"]))

    def test_uninspected_symlink_is_ambiguous(self) -> None:
        outside = Path(self.tmp.name) / "outside.txt"
        outside.write_text("legacyBilling\n", encoding="utf-8")
        link = self.root / "src" / "linked.ts"
        try:
            link.symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("symlink não disponível nesta plataforma")
        self.scan()
        payload = json.loads(self.ledger.read_text(encoding="utf-8"))
        match = next(item for item in payload["evidence"] if item["path"] == "src/linked.ts")
        self.assertEqual(match["status"], "ambiguous")
        self.assertEqual(match["class"], "symlink")

    def test_utf16_with_bom_is_scanned_instead_of_silently_skipped(self) -> None:
        encoded = self.root / "scripts" / "windows.ps1"
        encoded.write_text("LEGACY BILLING\n", encoding="utf-16")
        self.scan()
        payload = json.loads(self.ledger.read_text(encoding="utf-8"))
        match = next(item for item in payload["evidence"] if item["path"] == "scripts/windows.ps1")
        self.assertEqual(match["status"], "active")
        self.assertEqual(match["class"], "content-utf16")

    def test_utf16_without_bom_is_never_silently_green(self) -> None:
        small = self.root / "scripts" / "windows-no-bom.ps1"
        small.write_bytes("LEGACY BILLING\n".encode("utf-16-le"))
        large = self.root / "assets" / "windows-large.bin"
        large.parent.mkdir()
        large.write_bytes(("x" * 1_100_000 + "legacy billing").encode("utf-16-le"))

        self.scan()
        payload = json.loads(self.ledger.read_text(encoding="utf-8"))
        for relative in ("scripts/windows-no-bom.ps1", "assets/windows-large.bin"):
            with self.subTest(relative=relative):
                match = next(item for item in payload["evidence"] if item["path"] == relative)
                self.assertEqual(match["status"], "ambiguous")

    def test_fifo_is_ambiguous_without_blocking(self) -> None:
        if not hasattr(os, "mkfifo"):
            self.skipTest("FIFO não disponível nesta plataforma")
        fifo = self.root / "runtime.pipe"
        os.mkfifo(fifo)
        process = subprocess.Popen(
            [
                sys.executable,
                str(SCRIPT),
                "scan",
                "--root",
                str(self.root),
                "--target",
                "legacy billing",
                "--ledger",
                str(self.ledger),
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            stdout, stderr = process.communicate(timeout=1)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()
            self.fail("o auditor bloqueou ao tentar ler FIFO")
        self.assertEqual(process.returncode, 1, stderr)
        payload = json.loads(self.ledger.read_text(encoding="utf-8"))
        match = next(item for item in payload["evidence"] if item["path"] == "runtime.pipe")
        self.assertEqual(match["status"], "ambiguous")
        self.assertEqual(match["class"], "non-regular")
        self.assertTrue(stdout)

    def test_unreadable_file_is_ambiguous_instead_of_disappearing(self) -> None:
        unreadable = self.root / "assets" / "secret.bin"
        unreadable.parent.mkdir()
        unreadable.write_text("legacy billing\n", encoding="utf-8")
        unreadable.chmod(0)
        if os.access(unreadable, os.R_OK):
            unreadable.chmod(0o600)
            self.skipTest("chmod não tornou o arquivo ilegível nesta plataforma")
        try:
            self.scan()
        finally:
            unreadable.chmod(0o600)
        payload = json.loads(self.ledger.read_text(encoding="utf-8"))
        match = next(item for item in payload["evidence"] if item["path"] == "assets/secret.bin")
        self.assertEqual(match["status"], "ambiguous")
        self.assertEqual(match["class"], "path-unreadable")

    def test_ledger_must_be_regular_and_inside_root(self) -> None:
        outside = Path(self.tmp.name) / "outside" / "audit.json"
        external = self.run_cli(
            "scan",
            "--root",
            str(self.root),
            "--target",
            "legacy billing",
            "--ledger",
            str(outside),
        )
        self.assertEqual(external.returncode, 2)
        self.assertFalse(outside.exists())
        self.assertNotIn("Traceback", external.stderr)

        directory = self.root / "memory" / "audits" / "as-directory"
        directory.mkdir(parents=True)
        invalid = self.run_cli(
            "scan",
            "--root",
            str(self.root),
            "--target",
            "legacy billing",
            "--ledger",
            str(directory),
        )
        self.assertEqual(invalid.returncode, 2)
        self.assertNotIn("Traceback", invalid.stderr)

    def test_duplicate_validation_receipt_is_invalid(self) -> None:
        self.assertEqual(self.scan().returncode, 1)
        result = self.verify("--receipt", "unit=fail", "--receipt", "unit=pass")
        self.assertEqual(result.returncode, 2)
        self.assertIn("duplicado", result.stderr.lower())

    def test_large_file_streaming_finds_target_across_chunk_boundary(self) -> None:
        large = self.root / "assets" / "large.dat"
        large.parent.mkdir()
        prefix = b"x" * (64 * 1024 - 4)
        large.write_bytes(prefix + b"legacyBilling" + b"x" * (2 * 1024 * 1024))
        self.scan()
        payload = json.loads(self.ledger.read_text(encoding="utf-8"))
        match = next(item for item in payload["evidence"] if item["path"] == "assets/large.dat")
        self.assertEqual(match["status"], "ambiguous")
        self.assertEqual(match["class"], "content-large-file")

    def test_write_json_escapes_surrogate_paths_without_traceback(self) -> None:
        namespace = runpy.run_path(str(SCRIPT))
        payload = {"evidence": [{"path": "legacyBilling\udcff.ts"}]}

        namespace["write_json"](self.ledger, payload)

        written = json.loads(self.ledger.read_text(encoding="utf-8"))
        self.assertEqual(written, payload)

    def test_schema_declares_versioned_required_fields(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["schemaVersion"]["const"], "orq.audit-removal.v1")
        self.assertTrue({"target", "repository", "evidence", "verification"}.issubset(schema["required"]))


if __name__ == "__main__":
    unittest.main()
