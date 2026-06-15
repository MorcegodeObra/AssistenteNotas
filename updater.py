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

# Personal Access Token para repositórios privados.
# GitHub → Settings → Developer settings → Fine-grained tokens
# Permissões: Contents (read-only) + Metadata (read-only)
# Deixe "" para repositórios públicos.
GITHUB_TOKEN = ""

BG = "#1a1a2e"
FG = "white"
FG_DIM = "#aaaaaa"
FG_ERR = "#ff6b6b"
FG_OK = "#6bcb77"
BTN_BLUE = "#4a90d9"
BTN_BLUE_ACT = "#357abd"
BTN_RED = "#c0392b"
BTN_RED_ACT = "#922b21"
BTN_GRAY = "#444466"
BTN_GRAY_ACT = "#333355"


def get_current_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


def read_current_version(base_dir: Path) -> tuple[str, str]:
    """Retorna (versão, caminho_lido)."""
    vf = base_dir / VERSION_FILE
    if vf.exists():
        return vf.read_text(encoding="utf-8").strip(), str(vf)
    return "0.0.0", f"{vf} (não encontrado, assumindo 0.0.0)"


def parse_version(v: str) -> tuple:
    try:
        return tuple(int(x) for x in v.lstrip("v").strip().split("."))
    except ValueError:
        return (0, 0, 0)


def _gh_headers(accept: str = "application/vnd.github+json") -> dict:
    h = {"Accept": accept}
    if GITHUB_TOKEN and GITHUB_TOKEN != "SEU_TOKEN_AQUI":
        h["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return h


def get_latest_release() -> dict:
    resp = requests.get(GITHUB_API_URL, timeout=15, headers=_gh_headers())
    if resp.status_code == 404:
        raise RuntimeError(
            f"Nenhum release publicado em github.com/{GITHUB_REPO}.\n"
            "Crie e publique um release com AssistenteNotas.exe como asset.\n"
            "(Releases em modo Draft não aparecem aqui.)"
        )
    if resp.status_code == 401:
        raise RuntimeError(
            "Token inválido ou expirado.\n"
            "Gere um novo token em GitHub → Settings → Developer settings → Fine-grained tokens."
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
    # Para repos privados usa a URL da API com Accept: octet-stream;
    # para repos públicos usa a browser_download_url diretamente.
    if GITHUB_TOKEN and GITHUB_TOKEN != "SEU_TOKEN_AQUI":
        headers = _gh_headers("application/octet-stream")
    else:
        headers = {}
    resp = requests.get(url, stream=True, timeout=180, headers=headers)
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
        self.geometry("480x340")
        self.resizable(False, False)
        self.configure(bg=BG)

        self._base_dir = get_current_dir()
        self._current_version, self._version_path = read_current_version(self._base_dir)
        self._latest_tag: str = ""
        self._force = False

        self._build_ui()
        self.after(400, self._start_check)

    # ── UI ────────────────────────────────────────────────

    def _build_ui(self):
        self._title_lbl = tk.Label(
            self, text="Verificando atualizações...",
            bg=BG, fg=FG, font=("Segoe UI", 13, "bold"),
        )
        self._title_lbl.pack(pady=(20, 2))

        # Versão local + caminho
        self._ver_local_lbl = tk.Label(
            self,
            text=f"Versão instalada: {self._current_version}",
            bg=BG, fg=FG_DIM, font=("Segoe UI", 9),
        )
        self._ver_local_lbl.pack()

        self._ver_path_lbl = tk.Label(
            self,
            text=f"({self._version_path})",
            bg=BG, fg="#666688", font=("Segoe UI", 7),
            wraplength=460,
        )
        self._ver_path_lbl.pack()

        # Versão GitHub
        self._ver_gh_lbl = tk.Label(
            self, text="",
            bg=BG, fg=FG_DIM, font=("Segoe UI", 9),
        )
        self._ver_gh_lbl.pack(pady=(2, 0))

        # Status
        self._status_lbl = tk.Label(
            self, text="",
            bg=BG, fg=FG_DIM, font=("Segoe UI", 10),
            wraplength=440, justify="center",
        )
        self._status_lbl.pack(pady=(6, 2))

        # Barra de progresso
        self._progress = ttk.Progressbar(
            self, orient="horizontal", length=420, mode="determinate"
        )
        self._progress.pack(pady=(6, 4))

        # Botões
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(pady=10)

        self._force_btn = tk.Button(
            btn_row, text="Forçar atualização",
            state=tk.DISABLED,
            bg=BTN_GRAY, fg=FG,
            activebackground=BTN_GRAY_ACT, activeforeground=FG,
            relief=tk.FLAT, font=("Segoe UI", 9, "bold"),
            padx=12, pady=5, cursor="hand2",
            command=self._force_update,
        )
        self._force_btn.pack(side="left", padx=(0, 6))

        self._retry_btn = tk.Button(
            btn_row, text="Tentar novamente",
            state=tk.DISABLED,
            bg=BTN_RED, fg=FG,
            activebackground=BTN_RED_ACT, activeforeground=FG,
            relief=tk.FLAT, font=("Segoe UI", 9, "bold"),
            padx=12, pady=5, cursor="hand2",
            command=self._retry,
        )
        self._retry_btn.pack(side="left", padx=(0, 6))

        self._open_btn = tk.Button(
            btn_row, text="Abrir aplicativo",
            state=tk.DISABLED,
            bg=BTN_BLUE, fg=FG,
            activebackground=BTN_BLUE_ACT, activeforeground=FG,
            relief=tk.FLAT, font=("Segoe UI", 9, "bold"),
            padx=12, pady=5, cursor="hand2",
            command=self._open_app_and_close,
        )
        self._open_btn.pack(side="left")

        # Detalhe de erro
        self._detail_lbl = tk.Label(
            self, text="",
            bg=BG, fg=FG_ERR, font=("Segoe UI", 8),
            wraplength=460, justify="center",
        )
        self._detail_lbl.pack(pady=(0, 6))

    # ── Helpers de UI ─────────────────────────────────────

    def _set_title(self, text: str, color: str = FG):
        self._title_lbl.config(text=text, fg=color)

    def _set_status(self, text: str, color: str = FG_DIM):
        self._status_lbl.config(text=text, fg=color)

    def _set_detail(self, text: str):
        self._detail_lbl.config(text=text)

    def _set_gh_version(self, tag: str):
        self._ver_gh_lbl.config(text=f"Versão no GitHub: {tag}" if tag else "")

    def _set_progress(self, value: float):
        self._progress["value"] = value * 100

    def _enable_open(self):
        exists = (self._base_dir / APP_EXE_NAME).exists()
        self._open_btn.config(state=tk.NORMAL if exists else tk.DISABLED)

    def _enable_retry(self):
        self._retry_btn.config(state=tk.NORMAL)

    def _enable_force(self):
        self._force_btn.config(state=tk.NORMAL)

    def _disable_all(self):
        for btn in (self._force_btn, self._retry_btn, self._open_btn):
            btn.config(state=tk.DISABLED)

    # ── Fluxo ─────────────────────────────────────────────

    def _start_check(self):
        self._disable_all()
        self._set_detail("")
        self._set_progress(0)
        threading.Thread(target=self._check_and_update, daemon=True).start()

    def _retry(self):
        self._force = False
        self._set_title("Verificando atualizações...")
        self._set_status("Consultando GitHub...", FG_DIM)
        self._set_gh_version("")
        self._start_check()

    def _force_update(self):
        self._force = True
        self._disable_all()
        self._set_title("Forçando atualização...")
        self._set_status("Baixando versão mais recente...", FG_DIM)
        threading.Thread(target=self._check_and_update, daemon=True).start()

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

        self.after(0, lambda: self._set_gh_version(tag))

        already_up_to_date = parse_version(tag) <= parse_version(self._current_version)

        if already_up_to_date and not self._force:
            self.after(0, lambda: self._set_title("Aplicativo já está atualizado ✓", FG_OK))
            self.after(0, lambda: self._set_status(
                f"Versão instalada ({self._current_version}) = versão no GitHub ({tag}).", FG_DIM
            ))
            self.after(0, self._enable_open)
            self.after(0, self._enable_force)
            return

        asset = find_asset(release)
        if not asset:
            nomes = [a["name"] for a in release.get("assets", [])]
            self.after(0, lambda: self._set_title("Instalador não encontrado no release", FG_ERR))
            self.after(0, lambda: self._set_status(
                f"O arquivo '{APP_EXE_NAME}' não está no release {tag}.", FG_ERR
            ))
            detalhe = f"Assets encontrados: {', '.join(nomes)}" if nomes else "Nenhum asset no release."
            self.after(0, lambda: self._set_detail(detalhe))
            self.after(0, self._enable_open)
            self.after(0, self._enable_retry)
            return

        # ── Download ──────────────────────────────────────
        self.after(0, lambda: self._set_title(f"Baixando versão {tag}..."))
        tmp_path = self._base_dir / f"{APP_EXE_NAME}.tmp"

        def _progress(frac: float):
            pct = int(frac * 100)
            self.after(0, lambda: self._set_status(f"Baixando {tag}... {pct}%"))
            self.after(0, lambda: self._set_progress(frac))

        # Repo privado → URL da API (autenticada); público → URL direta
        dl_url = (
            asset["url"]
            if GITHUB_TOKEN and GITHUB_TOKEN != "SEU_TOKEN_AQUI"
            else asset["browser_download_url"]
        )
        download_file(dl_url, tmp_path, _progress)

        self.after(0, lambda: self._set_status("Encerrando versão anterior..."))
        kill_app()

        app_path = self._base_dir / APP_EXE_NAME
        if app_path.exists():
            app_path.unlink()
        tmp_path.rename(app_path)

        new_ver = tag.lstrip("v")
        (self._base_dir / VERSION_FILE).write_text(new_ver, encoding="utf-8")
        self._current_version = new_ver

        self.after(0, lambda: self._set_title("Atualização concluída! ✓", FG_OK))
        self.after(0, lambda: self._set_status(f"Versão {tag} instalada com sucesso.", FG_DIM))
        self.after(0, lambda: self._set_progress(1.0))
        self.after(0, self._enable_open)

    def _on_error(self, exc: Exception):
        msg = str(exc)
        if "for url" in msg:
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
