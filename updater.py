import sys
import os
import time
import threading
import subprocess
import requests
import tkinter as tk
from tkinter import ttk
from pathlib import Path

GITHUB_REPO = "MorcegodeObra/AssistenteNotas"
APP_EXE_NAME = "AssistenteNotas.exe"
VERSION_FILE = "version.txt"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


def get_current_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


def read_current_version(base_dir: Path) -> str:
    version_file = base_dir / VERSION_FILE
    if version_file.exists():
        return version_file.read_text(encoding="utf-8").strip()
    return "0.0.0"


def parse_version(v: str) -> tuple:
    v = v.lstrip("v").strip()
    try:
        return tuple(int(x) for x in v.split("."))
    except ValueError:
        return (0, 0, 0)


def get_latest_release() -> dict:
    resp = requests.get(
        GITHUB_API_URL,
        timeout=15,
        headers={"Accept": "application/vnd.github+json"},
    )
    resp.raise_for_status()
    return resp.json()


def find_asset(release: dict) -> dict | None:
    for asset in release.get("assets", []):
        if asset["name"] == APP_EXE_NAME:
            return asset
    return None


def download_file(url: str, dest: Path, progress_cb=None):
    resp = requests.get(url, stream=True, timeout=180)
    resp.raise_for_status()
    total = int(resp.headers.get("content-length", 0))
    downloaded = 0
    with open(dest, "wb") as f:
        for chunk in resp.iter_content(chunk_size=65536):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if progress_cb and total:
                    progress_cb(downloaded / total)


def kill_app():
    subprocess.run(
        ["taskkill", "/f", "/im", APP_EXE_NAME],
        capture_output=True,
    )
    time.sleep(1.5)


def launch_app(app_path: Path):
    subprocess.Popen([str(app_path)])


class UpdaterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Assistente Notas — Atualizador")
        self.geometry("440x200")
        self.resizable(False, False)
        self.configure(bg="#1a1a2e")

        self._base_dir = get_current_dir()
        self._current_version = read_current_version(self._base_dir)
        self._latest_tag: str = ""

        self._build_ui()
        self.after(400, self._start_check)

    def _build_ui(self):
        self._title_lbl = tk.Label(
            self,
            text="Verificando atualizações...",
            bg="#1a1a2e",
            fg="white",
            font=("Segoe UI", 13, "bold"),
        )
        self._title_lbl.pack(pady=(22, 4))

        self._status_lbl = tk.Label(
            self,
            text=f"Versão atual: {self._current_version}",
            bg="#1a1a2e",
            fg="#aaaaaa",
            font=("Segoe UI", 10),
        )
        self._status_lbl.pack()

        self._progress = ttk.Progressbar(
            self, orient="horizontal", length=380, mode="determinate"
        )
        self._progress.pack(pady=14)

        self._action_btn = tk.Button(
            self,
            text="Abrir aplicativo",
            state=tk.DISABLED,
            bg="#4a90d9",
            fg="white",
            activebackground="#357abd",
            activeforeground="white",
            relief=tk.FLAT,
            font=("Segoe UI", 10, "bold"),
            padx=24,
            pady=6,
            cursor="hand2",
            command=self._open_app_and_close,
        )
        self._action_btn.pack(pady=4)

    def _set_title(self, text: str):
        self._title_lbl.config(text=text)

    def _set_status(self, text: str):
        self._status_lbl.config(text=text)

    def _set_progress(self, value: float):
        self._progress["value"] = value * 100

    def _enable_open(self):
        self._action_btn.config(state=tk.NORMAL)

    def _start_check(self):
        threading.Thread(target=self._check_and_update, daemon=True).start()

    def _check_and_update(self):
        try:
            self._run_update_flow()
        except Exception as exc:
            self.after(0, lambda: self._on_error(str(exc)))

    def _run_update_flow(self):
        self.after(0, lambda: self._set_status("Consultando GitHub..."))

        release = get_latest_release()
        self._latest_tag = release.get("tag_name", "0.0.0")

        if parse_version(self._latest_tag) <= parse_version(self._current_version):
            self.after(0, lambda: self._set_title("Aplicativo já está atualizado"))
            self.after(
                0,
                lambda: self._set_status(
                    f"Versão {self._current_version} (mais recente disponível)"
                ),
            )
            self.after(0, self._enable_open)
            return

        asset = find_asset(release)
        if not asset:
            self.after(0, lambda: self._set_title(f"Update {self._latest_tag} disponível"))
            self.after(
                0,
                lambda: self._set_status("Arquivo de instalação não encontrado no release."),
            )
            self.after(0, self._enable_open)
            return

        # Download
        tag = self._latest_tag
        self.after(0, lambda: self._set_title(f"Baixando versão {tag}..."))
        tmp_path = self._base_dir / f"{APP_EXE_NAME}.tmp"

        def _progress(frac: float):
            self.after(0, lambda: self._set_status(f"Baixando... {int(frac * 100)}%"))
            self.after(0, lambda: self._set_progress(frac))

        download_file(asset["browser_download_url"], tmp_path, _progress)

        # Encerra o processo antigo
        self.after(0, lambda: self._set_status("Encerrando versão anterior..."))
        kill_app()

        # Substitui o executável
        app_path = self._base_dir / APP_EXE_NAME
        if app_path.exists():
            app_path.unlink()
        tmp_path.rename(app_path)

        # Atualiza version.txt
        (self._base_dir / VERSION_FILE).write_text(
            self._latest_tag.lstrip("v"), encoding="utf-8"
        )

        self.after(0, lambda: self._set_title("Atualização concluída!"))
        self.after(
            0,
            lambda: self._set_status(f"Versão {self._latest_tag} instalada com sucesso"),
        )
        self.after(0, lambda: self._set_progress(1.0))
        self.after(0, self._enable_open)

    def _on_error(self, msg: str):
        self._set_title("Erro ao verificar atualização")
        self._set_status(msg)
        self._enable_open()

    def _open_app_and_close(self):
        app_path = self._base_dir / APP_EXE_NAME
        if app_path.exists():
            launch_app(app_path)
        self.destroy()


if __name__ == "__main__":
    UpdaterApp().mainloop()