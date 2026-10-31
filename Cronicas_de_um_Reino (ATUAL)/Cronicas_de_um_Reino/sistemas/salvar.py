"""Salvar e carregar o progresso do personagem (com gravação segura e backup).

O arquivo é gravado primeiro em um temporário e só depois substitui o save antigo,
então uma falha no meio da gravação nunca corrompe o progresso. O save anterior
fica guardado em savegame.bak e é usado automaticamente se o principal estiver ruim.
"""
import json
import os
import traceback

PASTA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARQUIVO = os.path.join(PASTA, "savegame.json")
BACKUP = os.path.join(PASTA, "savegame.bak")
LOG_ERRO = os.path.join(PASTA, "erro.log")

# campos temporários de combate que não devem ir para o arquivo
_TEMPORARIOS = ("defendendo",)


def existe():
    return os.path.exists(ARQUIVO) or os.path.exists(BACKUP)


def salvar(jogador):
    """Grava o personagem. Nunca levanta exceção; retorna True se salvou."""
    try:
        dados = {k: v for k, v in jogador.items() if k not in _TEMPORARIOS}
        dados["versao"] = 2
        texto = json.dumps(dados, ensure_ascii=False, indent=2)
        tmp = ARQUIVO + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(texto)
            f.flush()
            os.fsync(f.fileno())
        if os.path.exists(ARQUIVO):
            try:
                os.replace(ARQUIVO, BACKUP)
            except OSError:
                pass
        os.replace(tmp, ARQUIVO)
        return True
    except Exception:
        registrar_erro("Falha ao salvar o jogo")
        return False


def _ler(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        dados = json.load(f)
    if not isinstance(dados, dict):
        raise ValueError("save inválido")
    return dados


def carregar():
    """Lê o save (ou o backup). Retorna o personagem já corrigido, ou None."""
    from sistemas import personagem   # import tardio para evitar ciclo
    for caminho in (ARQUIVO, BACKUP):
        if not os.path.exists(caminho):
            continue
        try:
            return personagem.garantir_campos(_ler(caminho))
        except Exception:
            registrar_erro(f"Falha ao ler {os.path.basename(caminho)}")
    return None


def registrar_erro(titulo):
    """Anota o erro em erro.log (para você poder me enviar depois)."""
    try:
        with open(LOG_ERRO, "a", encoding="utf-8") as f:
            f.write(f"=== {titulo} ===\n{traceback.format_exc()}\n")
    except OSError:
        pass
