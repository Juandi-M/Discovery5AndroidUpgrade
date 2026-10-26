import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location("grab_apps", Path(__file__).parents[1] / "tools/grab_apps.py")
grab = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(grab)


class GrabAppsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.adb = self.base / "adb"
        self.adb.touch()
        self.output = self.base / "capture"
        self.commands = []

    def fake_run(self, command, **kwargs):
        self.commands.append(command)
        args = command[3:]
        stdout, stderr, code = "", "", 0
        if args == ["get-state"]:
            stdout = "device\n"
        elif args[:3] == ["shell", "pm", "path"]:
            stdout = "package:/data/app/installed/base.apk\npackage:/data/app/installed/split_config.arm64.apk\n"
        elif args[0] == "pull":
            Path(args[2]).write_bytes(args[1].encode())
        elif "resolve-activity" in args:
            stdout = "com.example.launcher/.Home\n"
        return subprocess.CompletedProcess(command, code, stdout, stderr)

    def invoke(self, *args):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return grab.main(["--adb", str(self.adb), *args])

    def capture_args(self, *args):
        return ["--serial", "headunit:5555", "--output", str(self.output), *args]

    def manifest(self):
        return json.loads((self.output / "manifest.json").read_text())

    def test_explicit_target_required_before_any_adb_command(self):
        with patch.object(grab.subprocess, "run") as run:
            with self.assertRaises(SystemExit) as exc:
                self.invoke("--inventory")
            self.assertEqual(exc.exception.code, 2)
            run.assert_not_called()

    def test_rejects_package_injection_before_adb(self):
        with patch.object(grab.subprocess, "run") as run:
            with self.assertRaises(SystemExit):
                self.invoke("--serial", "headunit", "--package", "com.fake;reboot")
            run.assert_not_called()

    def test_split_apks_are_copied_and_hashed_and_commands_are_read_only(self):
        with patch.object(grab.subprocess, "run", side_effect=self.fake_run):
            status = self.invoke(*self.capture_args("--inventory", "--package", "com.example.zlink"))
        self.assertEqual(status, 0)
        manifest = self.manifest()
        self.assertEqual(manifest["status"], "complete")
        apks = manifest["packages"][0]["apks"]
        self.assertEqual(len(apks), 2)
        for apk in apks:
            raw = (self.output / apk["local_path"]).read_bytes()
            self.assertEqual(apk["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(apk["size_bytes"], len(raw))
            self.assertEqual(apk["status"], "copied")
        allowed = {"get-state", "pull"}
        allowed_shell = {"id", "getprop", "pm", "cmd", "dumpsys"}
        for command in self.commands:
            self.assertEqual(command[1:3], ["-s", "headunit:5555"])
            self.assertTrue(command[3] in allowed or
                            command[3] == "shell" and command[4] in allowed_shell)
            self.assertFalse(set(command) & {"root", "remount", "reboot", "install", "uninstall",
                                             "setprop", "push", "clear", "kill-server"})
            if command[3:5] == ["shell", "pm"]:
                self.assertIn(command[5], {"list", "path"})

    def test_permission_failure_preserves_partial_result_and_returns_nonzero(self):
        def deny_one(command, **kwargs):
            if command[3] == "pull" and "split_config" in command[4]:
                self.commands.append(command)
                return subprocess.CompletedProcess(command, 1, "", "Permission denied")
            return self.fake_run(command, **kwargs)
        with patch.object(grab.subprocess, "run", side_effect=deny_one):
            status = self.invoke(*self.capture_args("--package", "com.example.zlink"))
        self.assertEqual(status, 1)
        manifest = self.manifest()
        self.assertEqual(manifest["status"], "partial")
        self.assertIn("Permission denied", manifest["errors"][0]["message"])
        self.assertEqual([x["status"] for x in manifest["packages"][0]["apks"]], ["copied", "failed"])

    def test_timeout_is_recorded_and_stops_when_target_not_ready(self):
        with patch.object(grab.subprocess, "run", side_effect=subprocess.TimeoutExpired("adb", 30)):
            status = self.invoke(*self.capture_args("--inventory"))
        self.assertEqual(status, 1)
        manifest = self.manifest()
        self.assertEqual(len(manifest["commands"]), 1)
        self.assertEqual(manifest["commands"][0]["status"], "timeout")

    def test_existing_output_directory_is_not_overwritten(self):
        self.output.mkdir()
        sentinel = self.output / "keep.txt"
        sentinel.write_text("original")
        with patch.object(grab.subprocess, "run") as run:
            self.assertEqual(self.invoke(*self.capture_args("--inventory")), 2)
            run.assert_not_called()
        self.assertEqual(sentinel.read_text(), "original")

    def test_missing_or_unsafe_apk_paths_are_not_pulled(self):
        for index, stdout in enumerate(["Error: package inaccessible\n", "package:../../bad.apk\n"]):
            with self.subTest(stdout=stdout):
                self.output = self.base / f"invalid-path-{index}"
                self.commands = []
                def invalid_path(command, **kwargs):
                    if command[3:6] == ["shell", "pm", "path"]:
                        self.commands.append(command)
                        return subprocess.CompletedProcess(command, 0, stdout, "")
                    return self.fake_run(command, **kwargs)
                with patch.object(grab.subprocess, "run", side_effect=invalid_path):
                    status = self.invoke(*self.capture_args("--package", "com.example.zlink"))
                self.assertEqual(status, 1)
                self.assertEqual(self.manifest()["status"], "partial")
                self.assertFalse(any(command[3] == "pull" for command in self.commands))


if __name__ == "__main__":
    unittest.main()
