# -*- mode: python ; coding: utf-8 -*-
import os
import playwright

playwright_driver_path = os.path.join(os.path.dirname(playwright.__file__), "driver")

a = Analysis(
    ["app.py"],
    pathex=[],
    binaries=[],
    datas=[
        (playwright_driver_path, "playwright/driver"),
    ],
    hiddenimports=[
        "playwright",
        "playwright.sync_api",
        "playwright._impl._driver",
        "playwright._impl._api_types",
        "playwright._impl._browser",
        "playwright._impl._browser_context",
        "playwright._impl._page",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=["runtime_hook_playwright.py"],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="AssistenteNotas",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)