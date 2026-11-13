"""Exercise the actual installer only inside checkout-local isolated homes."""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Keep test homes and disposable source checkouts inside this repository.
ROOT = Path(__file__).resolve().parents[1]


class TestInstall(unittest.TestCase):
    """Check recursive discovery, repeatability, conflicts, and unsafe paths."""

    def setUp(self) -> None:
        """Allocate a private HOME and a disposable copy of the real payload."""
        temporary = tempfile.TemporaryDirectory(
            prefix=".install-test-", dir=ROOT
        )
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name)
        self.destination = self.home / ".copilot"
        self.checkout = self.home / "checkout"
        self.checkout.mkdir()
        shutil.copy2(ROOT / "install.py", self.checkout)
        shutil.copytree(ROOT / "instructions", self.checkout / "instructions")

    def run_install(
        self, *args: str, code: int = 0
    ) -> subprocess.CompletedProcess:
        """Invoke the CLI outside its checkout without using the real HOME."""
        result = subprocess.run(
            [sys.executable, "-B", str(self.checkout / "install.py"), *args],
            cwd=self.home,
            env={
                **os.environ,
                "HOME": str(self.home),
                "USERPROFILE": str(self.home),
                "PYTHONDONTWRITEBYTECODE": "1",
            },
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        if code:
            self.assertNotIn("Copied:", result.stdout)
        return result

    def test_dynamic_discovery_bytes_logging_and_idempotence(self) -> None:
        """Copy exact bytes and discover a newly added nested binary file."""
        sources = sorted(
            path
            for path in (self.checkout / "instructions").rglob("*")
            if path.is_file()
        )
        expected = [
            f"Copied: {source} -> "
            f"{self.destination / source.relative_to(self.checkout)}"
            for source in sources
        ]
        first = self.run_install()
        self.assertEqual(first.stdout.splitlines()[:-1], expected)
        installed = sorted(self.destination.rglob("*"))
        self.assertEqual(
            {path.relative_to(self.destination) for path in installed},
            {Path("instructions")}
            | {source.relative_to(self.checkout) for source in sources},
        )
        for source in sources:
            target = self.destination / source.relative_to(self.checkout)
            self.assertEqual(target.read_bytes(), source.read_bytes())
        before = {path: path.stat().st_mtime_ns for path in installed}
        for args in ((), ("--no-overwrite",)):
            rerun = self.run_install(*args)
            self.assertEqual(
                rerun.stdout.splitlines()[:-1],
                [line.replace("Copied:", "Unchanged:", 1) for line in expected],
            )
            self.assertIn(f"0 copied, {len(sources)} unchanged", rerun.stdout)
        self.assertEqual(
            {path: path.stat().st_mtime_ns for path in installed}, before
        )
        added = self.checkout / "instructions/future/deep/.payload.bin"
        added.parent.mkdir(parents=True)
        added.write_bytes(b"\x00verbatim\r\n\xff\n")
        target = self.destination / added.relative_to(self.checkout)
        output = self.run_install().stdout
        self.assertIn(f"Copied: {added} -> {target}\n", output)
        self.assertIn(f"1 copied, {len(sources)} unchanged", output)
        self.assertEqual(target.read_bytes(), added.read_bytes())

    def test_destination_overwrite_and_preflight_conflict(self) -> None:
        """Use a config root; preserve unrelated files and reject conflicts."""
        self.destination = self.home / "custom config"
        self.run_install("--destination", str(self.destination))
        target = self.destination / "instructions/testing.instructions.md"
        original = target.read_bytes()
        target.write_bytes(b"custom")
        missing = self.destination / "instructions/README.md"
        missing.unlink()
        keep = self.destination / "instructions/keep.txt"
        keep.write_bytes(b"unrelated")
        protected = self.run_install(
            "--destination", str(self.destination), "--no-overwrite", code=1
        )
        self.assertIn("Conflict:", protected.stderr)
        self.assertIn("omit --no-overwrite", protected.stderr)
        self.assertEqual(target.read_bytes(), b"custom")
        self.assertFalse(missing.exists())
        repaired = self.run_install("--destination", str(self.destination))
        self.assertIn("2 copied,", repaired.stdout)
        self.assertIn(f" -> {target}\n", repaired.stdout)
        self.assertEqual(target.read_bytes(), original)
        self.assertEqual(
            missing.read_bytes(),
            (self.checkout / "instructions/README.md").read_bytes(),
        )
        self.assertEqual(keep.read_bytes(), b"unrelated")
        self.assertFalse((self.home / ".copilot").exists())

    def test_unsafe_paths_fail_without_copying(self) -> None:
        """Reject linked sources/targets, hardlinks, traversal, and overlap."""
        outside = self.home / "outside"
        outside.mkdir()
        self.destination.symlink_to(outside, target_is_directory=True)
        self.assertIn("Linked path", self.run_install(code=1).stderr)
        self.assertEqual(list(outside.iterdir()), [])
        self.destination.unlink()
        for destination in (
            outside / "../escape",
            self.checkout / "nested",
            self.checkout,
            self.home,
        ):
            self.run_install("--destination", str(destination), code=1)
        self.assertFalse((self.home / "escape").exists())
        self.assertFalse((self.checkout / "nested").exists())
        self.destination.mkdir()
        instructions = self.destination / "instructions"
        instructions.symlink_to(outside, target_is_directory=True)
        self.run_install(code=1)
        self.assertEqual(list(outside.iterdir()), [])
        instructions.unlink()
        self.run_install()
        target = instructions / "testing.instructions.md"
        target.unlink()
        victim = outside / "keep.md"
        victim.write_bytes(b"keep")
        for link in ("symlink", "hardlink"):
            with self.subTest(link=link):
                if link == "symlink":
                    target.symlink_to(victim)
                else:
                    os.link(victim, target)
                for args in ((), ("--no-overwrite",)):
                    self.run_install(*args, code=1)
                target.unlink()
                self.assertEqual(victim.read_bytes(), b"keep")
        source = self.checkout / "instructions/testing.instructions.md"
        source.unlink()
        source.symlink_to(victim)
        fresh = self.home / "fresh"
        self.run_install("--destination", str(fresh), code=1)
        self.assertFalse(fresh.exists())


if __name__ == "__main__":
    unittest.main()
