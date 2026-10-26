#!/usr/bin/env python3
"""Copy installed head-unit apps and diagnostics through an existing ADB connection."""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


def now():
    return datetime.now(timezone.utc).isoformat()


def package_name(value):
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*", value):
        raise argparse.ArgumentTypeError("package must be an installed Android package name")
    return value


def adb_path(value):
    candidate = value or shutil.which("adb")
    if candidate is None:
        candidate = Path.home() / "Library/Android/sdk/platform-tools/adb"
    path = Path(candidate).expanduser()
    if not path.is_file():
        raise ValueError("ADB not found; use --adb /absolute/path/to/adb")
    return str(path.resolve())


def as_text(value):
    return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else (value or "")


def execute(command, timeout=30):
    result = {"command": command, "started_at": now()}
    try:
        completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8",
                                   errors="replace", timeout=timeout)
        result.update(returncode=completed.returncode, stdout=completed.stdout, stderr=completed.stderr)
        result["status"] = "ok" if completed.returncode == 0 else "error"
    except subprocess.TimeoutExpired as exc:
        result.update(returncode=124, status="timeout", stdout=as_text(exc.stdout),
                      stderr=as_text(exc.stderr) + "\nCommand timed out")
    except OSError as exc:
        result.update(returncode=127, status="error", stdout="", stderr=str(exc))
    result["finished_at"] = now()
    return result


class Capture:
    def __init__(self, adb, serial, output):
        self.adb, self.serial, self.output = adb, serial, output
        output.mkdir(parents=True, exist_ok=False, mode=0o700)
        self.data = {"started_at": now(), "serial": serial, "commands": [],
                     "packages": [], "errors": [], "status": "in_progress"}

    def error(self, operation, message):
        self.data["errors"].append({"operation": operation, "message": message})

    def run(self, *arguments, timeout=30):
        result = execute([self.adb, "-s", self.serial, *arguments], timeout)
        self.data["commands"].append(result)
        if result["status"] != "ok":
            self.error(" ".join(arguments), result["stderr"] or result["status"])
        return result

    def ready(self):
        result = self.run("get-state")
        if result["status"] == "ok" and result["stdout"].strip() == "device":
            return True
        if result["status"] == "ok":
            self.error("get-state", "Explicit target is not in authorized device state")
        return False

    def inventory(self):
        self.run("shell", "id")
        for prop in ["ro.build.version.release", "ro.build.version.sdk", "ro.build.fingerprint",
                     "ro.product.cpu.abi", "ro.product.cpu.abilist", "ro.product.board"]:
            self.run("shell", "getprop", prop)
        self.run("shell", "pm", "list", "packages", "-f")
        home = self.run("shell", "cmd", "package", "resolve-activity", "--brief",
                        "-a", "android.intent.action.MAIN", "-c", "android.intent.category.HOME")
        # Some older/vendor builds do not expose this command; preserve the failure.
        if home["status"] == "ok" and "/" not in home["stdout"]:
            self.error("resolve HOME", "No launchable HOME component returned")

    def extract(self, package):
        record = {"package": package, "apks": []}
        self.data["packages"].append(record)
        self.run("shell", "dumpsys", "package", package)
        response = self.run("shell", "pm", "path", package)
        if response["status"] != "ok":
            return
        paths = [line.removeprefix("package:").strip() for line in response["stdout"].splitlines()
                 if line.startswith("package:")]
        if not paths:
            self.error(f"pm path {package}", "No APK paths returned; package missing or inaccessible")
            return
        destination = self.output / "packages" / package
        destination.mkdir(parents=True, mode=0o700)
        for index, remote in enumerate(dict.fromkeys(paths)):
            item = {"remote_path": remote, "status": "failed", "sha256": None}
            record["apks"].append(item)
            path = PurePosixPath(remote)
            if not path.is_absolute() or ".." in path.parts or path.suffix != ".apk" or "\x00" in remote:
                self.error(f"pm path {package}", f"Unexpected APK path: {remote}")
                continue
            local = destination / f"{index:03d}.apk"
            item["local_path"] = str(local.relative_to(self.output))
            result = self.run("pull", remote, str(local), timeout=120)
            if result["status"] != "ok":
                continue
            if not local.is_file() or local.is_symlink():
                self.error(f"pull {remote}", "ADB returned success without a regular APK file")
                continue
            digest = hashlib.sha256()
            with local.open("rb") as source:
                for chunk in iter(lambda: source.read(1024 * 1024), b""):
                    digest.update(chunk)
            item.update(status="copied", size_bytes=local.stat().st_size, sha256=digest.hexdigest())

    def finish(self):
        self.data.update(finished_at=now(), status="partial" if self.data["errors"] else "complete")
        with (self.output / "manifest.json").open("x", encoding="utf-8") as manifest:
            json.dump(self.data, manifest, indent=2, ensure_ascii=False)
            manifest.write("\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adb", help="path to an existing ADB executable")
    parser.add_argument("--devices", action="store_true", help="list targets; does not select one")
    parser.add_argument("--serial", help="explicit head-unit serial or existing ADB network endpoint")
    parser.add_argument("--inventory", action="store_true", help="save build, package and HOME diagnostics")
    parser.add_argument("--package", action="append", type=package_name, default=[],
                        help="installed package to copy; repeat for launcher and ZLINK")
    parser.add_argument("--output", type=Path, help="new capture directory; existing paths are refused")
    args = parser.parse_args(argv)
    if args.devices and (args.inventory or args.package or args.serial or args.output):
        parser.error("--devices must be used alone (with optional --adb)")
    if not args.devices and not (args.inventory or args.package):
        parser.error("choose --devices, --inventory, or --package")
    if not args.devices and (not args.serial or args.serial.startswith("-") or
                             any(c.isspace() or ord(c) < 32 for c in args.serial)):
        parser.error("--serial must explicitly identify the head unit")
    try:
        adb = adb_path(args.adb)
        if args.devices:
            result = execute([adb, "devices", "-l"])
            print(result["stdout"], end="")
            if result["stderr"]:
                print(result["stderr"], file=sys.stderr, end="")
            return 0 if result["status"] == "ok" else 1
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
        output = args.output or (Path(__file__).resolve().parents[1] / ".local/captures" /
                                 f"{stamp}-{uuid.uuid4().hex[:8]}")
        capture = Capture(adb, args.serial, output.expanduser().resolve())
        try:
            if capture.ready():
                if args.inventory:
                    capture.inventory()
                for package in dict.fromkeys(args.package):
                    capture.extract(package)
        except OSError as exc:
            capture.error("local capture", str(exc))
        finally:
            capture.finish()
        print(f"Saved {capture.data['status']} capture: {capture.output}")
        return 1 if capture.data["errors"] else 0
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
