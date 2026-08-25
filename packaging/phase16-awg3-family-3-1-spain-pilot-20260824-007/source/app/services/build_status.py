from __future__ import annotations

import platform
from importlib import metadata
from typing import Any


def build_about_status() -> dict[str, Any]:
    return {
        "application": {
            "name": "amneziya",
            "version": _package_version("amneziya"),
            "source": "local package metadata",
        },
        "runtime": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "system": platform.system() or "unknown",
        },
        "build": {
            "status": "read-only",
            "auto_update": "No auto-update",
            "write_actions": "not available",
            "public_exposure": "not changed",
        },
        "blocked_surfaces": [
            "auto-update",
            "write API",
            "config delivery",
            "live peer apply/revoke",
            "backup/import/reboot",
            "public exposure",
        ],
    }


def _package_version(package_name: str) -> str:
    try:
        return metadata.version(package_name)
    except metadata.PackageNotFoundError:
        return "unknown"
