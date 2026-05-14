import sys

if getattr(sys, "frozen", False):
    from pathlib import Path
    import playwright._impl._driver as _driver

    _meipass = Path(sys._MEIPASS)

    # compute_driver_executable() deve retornar (node_exe: str, cli_js: str)
    def _patched_compute():
        node_exe = str(_meipass / "playwright" / "driver" / "node.exe")
        cli_js = str(_meipass / "playwright" / "driver" / "package" / "cli.js")
        return (node_exe, cli_js)

    _driver.compute_driver_executable = _patched_compute