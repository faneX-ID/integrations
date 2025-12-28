#!/usr/bin/env python3
"""
Generate components overview README for integrations repository.
Scans all integration directories and generates a comprehensive overview.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).parent.parent.parent


def load_manifest(integration_dir: Path) -> Optional[Dict]:
    """Load and parse manifest.json from an integration directory."""
    manifest_path = integration_dir / "manifest.json"
    if not manifest_path.exists():
        return None

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Failed to load manifest from {integration_dir}: {e}")
        return None


def get_integration_directories() -> List[Path]:
    """Get all integration directories."""
    integrations = []
    for item in REPO_ROOT.iterdir():
        if item.is_dir() and not item.name.startswith(".") and item.name != "node_modules":
            manifest_path = item / "manifest.json"
            if manifest_path.exists():
                integrations.append(item)
    return sorted(integrations, key=lambda x: x.name.lower())


def format_capabilities(capabilities: List[str]) -> str:
    """Format capabilities list."""
    if not capabilities:
        return "-"
    return ", ".join(f"`{cap}`" for cap in capabilities)


def format_requirements(requirements: List[str]) -> str:
    """Format requirements list."""
    if not requirements:
        return "-"
    # Truncate if too long
    req_str = ", ".join(requirements)
    if len(req_str) > 60:
        return req_str[:57] + "..."
    return req_str


def generate_overview() -> str:
    """Generate the components overview README."""
    integrations = get_integration_directories()
    manifests = []

    for integration_dir in integrations:
        manifest = load_manifest(integration_dir)
        if manifest:
            manifests.append((integration_dir.name, manifest))

    # Sort by name
    manifests.sort(key=lambda x: x[1].get("name", x[0]).lower())

    # Generate README
    lines = [
        "# 🛒 faneX-ID Standard Integrations",
        "",
        "[![Addon Validation](https://github.com/faneX-ID/integrations/actions/workflows/ci.yml/badge.svg)](https://github.com/faneX-ID/integrations/actions/workflows/ci.yml)",
        "",
        "> **Official System Integrations** for [faneX-ID Core](https://github.com/faneX-ID/core). 🔐",
        "",
        "This repository hosts the certified, battery-included integrations that ship (or are available) for faneX-ID.",
        "",
        "---",
        "",
        "## 📦 Available Integrations",
        "",
        f"**Total: {len(manifests)} integrations**",
        "",
        "| Name | Version | Description | Capabilities | Requirements |",
        "|------|---------|-------------|--------------|--------------|",
    ]

    for dir_name, manifest in manifests:
        name = manifest.get("name", dir_name)
        version = manifest.get("version", "N/A")
        description = manifest.get("description", "-")
        # Truncate description if too long
        if len(description) > 80:
            description = description[:77] + "..."
        capabilities = format_capabilities(manifest.get("capabilities", []))
        requirements = format_requirements(manifest.get("requirements", []))

        # Escape pipe characters in markdown table
        name = name.replace("|", "\\|")
        description = description.replace("|", "\\|")

        lines.append(f"| [{name}]({dir_name}/) | {version} | {description} | {capabilities} | {requirements} |")

    lines.extend([
        "",
        "## 📂 Repository Structure",
        "",
        "*   `📜 addons.json` — The central index file read by faneX-ID Core.",
        "*   Each integration directory contains:",
        "    *   `manifest.json` — Integration metadata and configuration schema",
        "    *   `integration.py` or `integration.ps1` — Implementation file",
        "    *   `README.md` — Integration documentation",
        "",
        "## 🚀 Getting Started",
        "",
        "To utilize these integrations, ensure your faneX-ID instance is configured to use this repository (default setting).",
        "",
        "## 🤝 Contributing",
        "",
        "We welcome contributions! Please refer to the [🧩 Integration Development Guide](https://github.com/faneX-ID/core/blob/main/INTEGRATION_DEV_GUIDE.md) before submitting Pull Requests.",
        "",
        "## 📝 License",
        "",
        "This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0) - see the [LICENSE](LICENSE) file for details.",
        "",
        f"---",
        f"",
        f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}*",
    ])

    return "\n".join(lines)


def main():
    """Main function."""
    overview = generate_overview()
    readme_path = REPO_ROOT / "README.md"

    # Write README
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(overview)

    print(f"✅ Generated components overview with {len(get_integration_directories())} integrations")
    print(f"📝 Updated {readme_path}")


if __name__ == "__main__":
    main()
