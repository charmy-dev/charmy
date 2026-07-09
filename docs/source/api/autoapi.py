"""
Auto-generate Charmy API documentation (.rst) from the ``charmy`` package source.

Usage
-----
Run from **project root**::

    python docs/source/api/autoapi.py

Or from **anywhere** if ``charmy/`` package is discoverable::

    python path/to/docs/source/api/autoapi.py

What it does
------------
1. Scans every ``.py`` file in the ``charmy/`` package (recursively).
2. Generates an ``.rst`` file for each module, following the existing manual
   pattern (``autoclasstree`` + ``automodule``).
3. Generates an ``index.rst`` with ``toctree`` for every subpackage that has
   children.
4. Skips trivial / non-API files (``skhynix.py``, ``text.py``, ``__main__.py``).

Some existing inaccurate docs (``pos.rst``, ``rect.rst``, ``size.rst``,
``color.rst``, ``canvas.rst``, ``frameworks/``) reference modules that no
longer exist — this script will **not** re-create them, keeping the tree clean.

Check it in once, tweak the exclusion list over time, profit.
"""

# ── stdlib ──────────────────────────────────────────────────────────────────
import os
import sys
from pathlib import Path
from typing import Iterator

# ── Paths ───────────────────────────────────────────────────────────────────

#: Location of *this* script (used to derive everything else).
_SCRIPT_DIR = Path(__file__).parent.resolve()

#: Output root — same as script location (``docs/source/api/``).
_OUTPUT_DIR = _SCRIPT_DIR

#: Scan every file under ``charmy/``
_PACKAGE_NAME = "charmy"
_PROJECT_ROOT: Path | None = None  # resolved below


def _find_project_root() -> Path:
    """Walk up from script dir until we find ``charmy/`` + ``pyproject.toml``."""
    candidate = _SCRIPT_DIR
    for _ in range(12):  # sane upper bound
        if (candidate / _PACKAGE_NAME).is_dir() and (
            candidate / "pyproject.toml"
        ).is_file():
            return candidate
        candidate = candidate.parent
    raise RuntimeError(
        f"Could not locate project root (no {_PACKAGE_NAME}/ with "
        f"pyproject.toml found above {_SCRIPT_DIR})"
    )


_PROJECT_ROOT = _find_project_root()
_PACKAGE_ROOT = _PROJECT_ROOT / _PACKAGE_NAME

# ── Exclusions ──────────────────────────────────────────────────────────────

#: Dotted module paths that should NEVER get an ``.rst`` file.
_SKIP_MODULES: frozenset[str] = frozenset({
    f"{_PACKAGE_NAME}.widgets.skhynix",  # easter egg (intentionally raises)
    f"{_PACKAGE_NAME}.widgets.text",      # empty stub
    f"{_PACKAGE_NAME}.__main__",           # entry point, not API
    f"{_PACKAGE_NAME}._compat",            # safety valve for future use
})

#: Sub-packages whose ``__init__.py`` should be treated as "just a namespace"
#: and **not** get their own ``.. automodule::`` section.  Their ``index.rst``
#: will only have the toctree.
_SKIP_AUTOMODULE_PACKAGES: frozenset[str] = frozenset()

#: (display_name → source_name) overrides when the RST filename MUST differ
#: from the last component of the module path.
_NAME_OVERRIDES: dict[str, str] = {
    "object": "cm_object",  # charmy/cm_object.py → object.rst
}

# ── Module discovery ────────────────────────────────────────────────────────


def _discover_modules(root: Path) -> list[tuple[str, Path]]:
    """Yield ``(dotted_path, file_path)`` for every ``.py`` file under *root*."""
    results: list[tuple[str, Path]] = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune irrelevant directories
        dirnames[:] = [
            d for d in dirnames
            if not d.startswith(".") and d != "__pycache__"
        ]
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            fp = Path(dirpath) / fn
            rel = fp.relative_to(_PROJECT_ROOT)
            dotted = str(rel.with_suffix("")).replace(os.sep, ".")
            results.append((dotted, fp))
    return results


# ── Helpers ─────────────────────────────────────────────────────────────────


def _short_name(dotted: str) -> str:
    """Last component, possibly overridden via ``_NAME_OVERRIDES``."""
    name = dotted.rsplit(".", 1)[-1]
    for display, source in _NAME_OVERRIDES.items():
        if name == source:
            return display
    return name


def _target_rst_path(dotted: str) -> Path:
    """Where the ``.rst`` file for *dotted* should live."""
    parts = dotted.split(".")
    # last part = module name; everything before = subpackage path
    name = _short_name(dotted)
    if len(parts) == 1:
        return _OUTPUT_DIR / f"{name}.rst"
    # e.g. "charmy.widgets.button" → OUTPUT/widgets/button.rst
    return _OUTPUT_DIR.joinpath(*parts[1:-1], f"{name}.rst")


def _is_init(dotted: str) -> bool:
    return dotted.endswith(".__init__")


def _package_of(dotted: str) -> str:
    """Return the package portion of a module path.

    ``"charmy.widgets.button"`` → ``"charmy.widgets"``
    ``"charmy"`` → ``""``
    """
    pkg = dotted.rsplit(".", 1)[0] if "." in dotted else ""
    return pkg


# ── RST templates ───────────────────────────────────────────────────────────


def _module_rst(dotted: str, short: str) -> str:
    """RST for a single module."""
    title = short
    sep = "=" * len(title)

    # Skip autoclasstree for backend modules — the mermaid autoclassdiag
    # crashes on genesis's circular class refs (Backend ↔ *Base ↔ Backend)
    # even with the conf.py skip hook, because it imports and traverses
    # full class hierarchies.
    if ".backend." in dotted or dotted.endswith(".backend"):
        tree_block = (
            f".. autoclasstree:: {dotted}\n"
            f"\n"
        )
    else:
        tree_block = (
            f".. autoclasstree:: {dotted}\n"
            f"   :full:\n"
            f"   :strict:\n"
            f"\n"
        )
    return (
        f"{title}\n"
        f"{sep}\n"
        f"\n"
        f"{tree_block}"
        f".. automodule:: {dotted}\n"
        f"   :members:\n"
    )


def _package_index_rst(
    pkg_dotted: str,
    children: list[tuple[str, str, str]],
    *,
    include_automodule: bool = True,
) -> str:
    """RST for a sub-package index (generated for ``__init__.py``).

    Each child is ``(display_name, dotted_path, toctree_entry)``.
    """
    title = pkg_dotted
    sep = "=" * len(title)
    lines = [title, sep, ""]

    # autoclasstree — skip :full:/:strict: for backend to avoid mermaid
    # autoclassdiag crash on circular class refs.
    is_backend = ".backend" in pkg_dotted or pkg_dotted.endswith(".backend")
    lines.append(f".. autoclasstree:: {pkg_dotted}")
    if not is_backend:
        lines.append("   :full:")
    lines.append("   :strict:")
    lines.append("")

    if include_automodule:
        lines += [
            f".. automodule:: {pkg_dotted}",
            "   :members:",
            "",
        ]
    lines += [
        ".. toctree::",
        "   :maxdepth: 2",
        "",
    ]
    for display_name, _dotted, toctree_entry in sorted(
            children, key=lambda x: x[0]):
        lines.append(f"   {toctree_entry}")
    lines.append("")
    return "\n".join(lines)


# ── Main ────────────────────────────────────────────────────────────────────


def _package_hierarchy(modules: list[tuple[str, Path]]) \
        -> dict[str, dict[str, list[tuple[str, str]]]]:
    """Build a package → children mapping.

    Returns ``{pkg_dotted: {"leaves": [(name, dotted, toctree_path), ...],
                            "subpkgs": [(name, pkg_dotted, toctree_path), ...]}}``
    """
    # Separate inits and leaves
    inits: dict[str, Path] = {}
    leaves: list[tuple[str, Path]] = []
    for dotted, path in modules:
        if _is_init(dotted):
            inits[dotted[: -len(".__init__")]] = path
        else:
            leaves.append((dotted, path))

    # Gather direct leaf children per package
    result: dict[str, dict] = {}
    for pkg in inits:
        result.setdefault(pkg, {"leaves": [], "subpkgs": [],
                                "path": inits[pkg]})

    for dotted, _ in leaves:
        pkg = _package_of(dotted)
        if pkg in result:
            name = _short_name(dotted)
            result[pkg]["leaves"].append((name, dotted, name))

    # Assign sub-packages: pkgX is a sub-package of pkgY iff
    # pkgY = parent(pkgX) and pkgX != pkgY
    for pkg_a in inits:
        parent = _package_of(pkg_a)
        if parent in result:
            sub_name = pkg_a.rsplit(".", 1)[-1]
            # Sub-package toctree entry must point to its index.rst
            result[parent]["subpkgs"].append(
                (sub_name, pkg_a, f"{sub_name}/index"))

    return result


def main():
    print(f"[SCAN]  Scanning package: {_PACKAGE_ROOT}")
    raw_modules = _discover_modules(_PACKAGE_ROOT)
    print(f"        Found {len(raw_modules)} .py files")

    # Filter excluded
    modules = [(d, p) for d, p in raw_modules if d not in _SKIP_MODULES]

    # Separate package-inits from leaf modules
    leaf_modules: list[tuple[str, Path]] = []
    for dotted, path in modules:
        if not _is_init(dotted):
            leaf_modules.append((dotted, path))

    # Build package hierarchy (inits discovered automatically)
    hierarchy = _package_hierarchy(modules)

    # ── 1. Generate per-module RST files ────────────────────────────────
    mod_count = 0
    for dotted, _ in leaf_modules:
        rst_path = _target_rst_path(dotted)
        rst_path.parent.mkdir(parents=True, exist_ok=True)
        content = _module_rst(dotted, _short_name(dotted))
        rst_path.write_text(content, encoding="utf-8")
        print(f"   [FILE]  {rst_path.relative_to(_OUTPUT_DIR)}  <-  {dotted}")
        mod_count += 1

    # ── 2. Generate per-package index.rst from __init__.py ──────────────
    pkg_count = 0
    for pkg_dotted, info in hierarchy.items():
        # Combine leaves + sub-packages into one sorted toctree list
        children: list[tuple[str, str, str]] = info["leaves"] + info["subpkgs"]
        children.sort(key=lambda x: x[0])  # alphabetical

        if not children:
            continue  # empty namespace — skip

        out_dir = _OUTPUT_DIR.joinpath(*pkg_dotted.split(".")[1:])
        rst_path = out_dir / "index.rst"
        rst_path.parent.mkdir(parents=True, exist_ok=True)

        include_auto = pkg_dotted not in _SKIP_AUTOMODULE_PACKAGES
        content = _package_index_rst(pkg_dotted, children,
                                     include_automodule=include_auto)
        rst_path.write_text(content, encoding="utf-8")
        print(f"   [DIR]   {rst_path.relative_to(_OUTPUT_DIR)}  <-  package {pkg_dotted}")
        pkg_count += 1

    # ── Summary ─────────────────────────────────────────────────────────
    total = mod_count + pkg_count
    print()
    print(f"   [DONE]  {total} file(s) generated ({mod_count} modules, "
          f"{pkg_count} package indices)")
    print(f"   [OUT]   {_OUTPUT_DIR}")

    # ── Advice for stale docs that won't be regenerated ─────────────────
    all_dotted_modules = {d for d, _ in leaf_modules}
    all_packages = set(hierarchy.keys())

    stale_docs: list[str] = []
    # Walk output tree looking for .rst files whose module no longer exists
    existing_rsts = sorted(_OUTPUT_DIR.rglob("*.rst"))
    for rp in existing_rsts:
        if rp.name in ("index.rst",):
            continue  # package index files are handled separately
        # Map back to a hypothetical module path
        rel = rp.relative_to(_OUTPUT_DIR)
        parts = list(rel.with_suffix("").parts)
        candidate = f"{_PACKAGE_NAME}.{'.'.join(parts)}"
        # Check if any existing module would generate this file
        if candidate not in all_dotted_modules:
            # Check name overrides in reverse
            overridden = False
            for display, source in _NAME_OVERRIDES.items():
                if candidate.endswith(display):
                    alt = candidate.rsplit(display, 1)[0] + source
                    if alt in all_dotted_modules:
                        overridden = True
                        break
            if not overridden:
                stale_docs.append(str(rel))

    if stale_docs:
        print()
        print("   [WARN]  Stale RST files (module no longer exists):")
        for s in stale_docs:
            print(f"           . {s}")
        print(f"           -> Consider removing or updating them manually.")


if __name__ == "__main__":
    main()
