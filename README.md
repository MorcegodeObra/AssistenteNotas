# AssistenteNotas — Emissor de NFS-e

Aplicativo de desktop para emissão de **Notas Fiscais de Serviço Eletrônicas (NFS-e)**.  
Com ele você cadastra prestadores, tomadores e modelos de nota padrão, e emite notas fiscais diretamente pelo computador com poucos cliques.

---

## O que você precisa para usar

Escolha **uma** das duas opções abaixo:

| Opção | Quando usar |
|---|---|
| **Executável (.exe)** | Quer só usar o programa, sem instalar nada |
| **Código-fonte (Python)** | Quer modificar o programa ou contribuir |

---

## Opção 1 — Usar o executável (mais fácil)

> Não precisa instalar nada. Basta ter o Windows.

1. Navegue até a pasta `dist\AssistenteNotas\`
2. Dê um duplo clique em **`AssistenteNotas.exe`**
3. O programa abre imediatamente

---

## Opção 2 — Rodar pelo código-fonte (Python)

### Pré-requisitos

- **Python 3.11 ou superior** — Baixe em [python.org/downloads](https://www.python.org/downloads/)  
  > Durante a instalação, marque a opção **"Add Python to PATH"**

### Passo a passo

Abra o **Prompt de Comando** (pressione `Win + R`, digite `cmd` e pressione Enter) e execute os comandos abaixo um por um:

```bash
# 1. Vá até a pasta do projeto (ajuste o caminho se necessário)
cd C:\Repos\AssistenteNotas

# 2. Crie um ambiente virtual (isola as dependências)
python -m venv venv

# 3. Ative o ambiente virtual
venv\Scripts\activate

# 4. Instale as dependências
pip install customtkinter requests playwright

# 5. Instale os navegadores do Playwright
python -m playwright install chromium

# 6. Inicie o programa
python app.py
```

---

## Configuração da API

O aplicativo se conecta a uma API para salvar e carregar os dados.  
Por padrão, ele usa a API hospedada em `https://sistemanotas-goba.onrender.com`.

Se você tiver uma API própria rodando localmente, edite o arquivo `config/api.py` e altere a linha:

```python
BASE_URL = "https://sistemanotas-goba.onrender.com"
```

Substitua pelo endereço da sua API, por exemplo: `http://localhost:3000`

---

## Como usar o programa

1. **Login** — Na tela inicial, insira seu usuário e senha cadastrados na API
2. **Prestador** — Cadastre ou atualize os dados do prestador de serviços
3. **Tomadores** — Adicione os clientes que receberão as notas
4. **Notas Padrão** — Crie modelos de nota para agilizar a emissão
5. **Emitir Nota** — Selecione o tomador e o modelo e emita a nota com um clique

---

## Problemas comuns

| Problema | Solução |
|---|---|
| `python` não é reconhecido | Reinstale o Python marcando "Add Python to PATH" |
| Erro de conexão ao fazer login | Verifique se a URL da API em `config/api.py` está correta |
| Tela não abre | Tente rodar `python app.py` no terminal para ver a mensagem de erro |
