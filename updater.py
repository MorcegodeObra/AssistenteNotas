import sys
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

BG = "#1a1a2e"
FG = "white"
FG_DIM = "#aaaaaa"
FG_ERR = "#ff6b6b"
FG_OK = "#6bcb77"
BTN_BLUE = "#4a90d9"
BTN_BLUE_ACT = "#357abd"
BTN_RED = "#c0392b"
BTN_RED_ACT = "#922b21"


def get_current_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


def read_current_version(base_dir: Path) -> str:
    vf = base_dir / VERSION_FILE
    return vf.read_text(encoding="utf-8").strip() if vf.exists() else "0.0.0"


def parse_version(v: str) -> tuple:
    try:
        return tuple(int(x) for x in v.lstrip("v").strip().split("."))
    except ValueError:
        return (0, 0, 0)


def get_latest_release() -> dict:
    resp = requests.get(
        GITHUB_API_URL,
        timeout=15,
        headers={"Accept": "application/vnd.github+json"},
    )
    if resp.status_code == 404:
        raise RuntimeError(
            "Nenhuma versão publicada no GitHub ainda.\n"
            f"Repositório: {GITHUB_REPO}"
        )
    if resp.status_code == 403:
        raise RuntimeError("Limite de requisições da API do GitHub atingido. Aguarde alguns minutos.")
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
    subprocess.run(["taskkill", "/f", "/im", APP_EXE_NAME], capture_output=True)
    time.sleep(1.5)


def launch_app(app_path: Path):
    subprocess.Popen([str(app_path)])


class UpdaterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Assistente Notas — Atualizador")
        self.geometry("460x300")
        self.resizable(False, False)
        self.configure(bg=BG)

        self._base_dir = get_current_dir()
        self._current_version = read_current_version(self._base_dir)
        self._latest_tag: str = ""

        self._build_ui()
        self.after(400, self._start_check)

    # ── UI ────────────────────────────────────────────────

    def _build_ui(self):
        # Título
        self._title_lbl = tk.Label(
            self, text="Verificando atualizações...",
            bg=BG, fg=FG, font=("Segoe UI", 13, "bold"),
        )
        self._title_lbl.pack(pady=(24, 4))

        # Versão atual
        tk.Label(
            self, text=f"Versão instalada: {self._current_version}",
            bg=BG, fg=FG_DIM, font=("Segoe UI", 9),
        ).pack()

        # Status (multi-linha, envolve texto longo)
        self._status_lbl = tk.Label(
            self, text="",
            bg=BG, fg=FG_DIM, font=("Segoe UI", 10),
            wraplength=420, justify="center",
        )
        self._status_lbl.pack(pady=(8, 2))

        # Barra de progresso
        self._progress = ttk.Progressbar(
            self, orient="horizontal", length=400, mode="determinate"
        )
        self._progress.pack(pady=(8, 4))

        # Linha de botões
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(pady=12)

        self._retry_btn = tk.Button(
            btn_row, text="Tentar novamente",
            state=tk.DISABLED,
            bg=BTN_RED, fg=FG,
            activebackground=BTN_RED_ACT, activeforeground=FG,
            relief=tk.FLAT, font=("Segoe UI", 10, "bold"),
            padx=16, pady=6, cursor="hand2",
            command=self._retry,
        )
        self._retry_btn.pack(side="left", padx=(0, 8))

        self._open_btn = tk.Button(
            btn_row, text="Abrir aplicativo",
            state=tk.DISABLED,
            bg=BTN_BLUE, fg=FG,
            activebackground=BTN_BLUE_ACT, activeforeground=FG,
            relief=tk.FLAT, font=("Segoe UI", 10, "bold"),
            padx=16, pady=6, cursor="hand2",
            command=self._open_app_and_close,
        )
        self._open_btn.pack(side="left")

        # Detalhes de erro (oculto por padrão)
        self._detail_lbl = tk.Label(
            self, text="",
            bg=BG, fg=FG_ERR, font=("Segoe UI", 8),
            wraplength=420, justify="center",
        )
        self._detail_lbl.pack(pady=(0, 8))

    # ── Helpers de UI (thread-safe via after) ─────────────

    def _set_title(self, text: str, color: str = FG):
        self._title_lbl.config(text=text, fg=color)

    def _set_status(self, text: str, color: str = FG_DIM):
        self._status_lbl.config(text=text, fg=color)

    def _set_detail(self, text: str):
        self._detail_lbl.config(text=text)

    def _set_progress(self, value: float):
        self._progress["value"] = value * 100

    def _enable_open(self):
        app_exists = (self._base_dir / APP_EXE_NAME).exists()
        self._open_btn.config(state=tk.NORMAL if app_exists else tk.DISABLED)

    def _enable_retry(self):
        self._retry_btn.config(state=tk.NORMAL)

    # ── Fluxo principal ───────────────────────────────────

    def _start_check(self):
        self._retry_btn.config(state=tk.DISABLED)
        self._open_btn.config(state=tk.DISABLED)
        self._set_detail("")
        self._set_progress(0)
        threading.Thread(target=self._check_and_update, daemon=True).start()

    def _retry(self):
        self._set_title("Verificando atualizações...")
        self._set_status("Consultando GitHub...", FG_DIM)
        self._start_check()

    def _check_and_update(self):
        try:
            self._run_update_flow()
        except Exception as exc:
            self.after(0, lambda: self._on_error(exc))

    def _run_update_flow(self):
        self.after(0, lambda: self._set_status("Consultando GitHub..."))

        release = get_latest_release()
        self._latest_tag = release.get("tag_name", "0.0.0")
        tag = self._latest_tag

        self.after(0, lambda: self._set_status(f"Última versão disponível: {tag}"))

        if parse_version(tag) <= parse_version(self._current_version):
            self.after(0, lambda: self._set_title("Aplicativo já está atualizado ✓", FG_OK))
            self.after(0, lambda: self._set_status(f"Versão {self._current_version} é a mais recente.", FG_DIM))
            self.after(0, self._enable_open)
            return

        asset = find_asset(release)
        if not asset:
            nomes = [a["name"] for a in release.get("assets", [])]
            detalhe = (
                f"Assets no release: {', '.join(nomes)}"
                if nomes else "Nenhum asset encontrado no release."
            )
            self.after(0, lambda: self._set_title(f"Update {tag} disponível, mas sem instalador"))
            self.after(0, lambda: self._set_status(
                f"O arquivo '{APP_EXE_NAME}' não foi encontrado no release {tag}.", FG_ERR
            ))
            self.after(0, lambda: self._set_detail(detalhe))
            self.after(0, self._enable_open)
            self.after(0, self._enable_retry)
            return

        # Download
        self.after(0, lambda: self._set_title(f"Baixando versão {tag}..."))
        tmp_path = self._base_dir / f"{APP_EXE_NAME}.tmp"

        def _progress(frac: float):
            pct = int(frac * 100)
            self.after(0, lambda: self._set_status(f"Baixando {tag}... {pct}%"))
            self.after(0, lambda: self._set_progress(frac))

        download_file(asset["browser_download_url"], tmp_path, _progress)

        self.after(0, lambda: self._set_status("Encerrando versão anterior..."))
        kill_app()

        app_path = self._base_dir / APP_EXE_NAME
        if app_path.exists():
            app_path.unlink()
        tmp_path.rename(app_path)

        (self._base_dir / VERSION_FILE).write_text(tag.lstrip("v"), encoding="utf-8")

        self.after(0, lambda: self._set_title(f"Atualização concluída! ✓", FG_OK))
        self.after(0, lambda: self._set_status(f"Versão {tag} instalada com sucesso.", FG_DIM))
        self.after(0, lambda: self._set_progress(1.0))
        self.after(0, self._enable_open)

    def _on_error(self, exc: Exception):
        msg = str(exc)
        # Simplifica mensagens HTTP longas
        if "HTTPError" in type(exc).__name__ and "for url" in msg:
            msg = msg.split(" for url")[0]
        self._set_title("Erro ao verificar atualização", FG_ERR)
        self._set_status(msg, FG_ERR)
        self._set_detail(f"Repositório: github.com/{GITHUB_REPO}")
        self._enable_open()
        self._enable_retry()

    def _open_app_and_close(self):
        app_path = self._base_dir / APP_EXE_NAME
        if app_path.exists():
            launch_app(app_path)
        self.destroy()


if __name__ == "__main__":
    UpdaterApp().mainloop()
