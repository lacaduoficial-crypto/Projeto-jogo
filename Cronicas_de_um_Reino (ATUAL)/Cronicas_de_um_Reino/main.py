import pygame

from inimigos.inimigos import inimigo_aleatorio, tela_bestiario
from mapas.mapa import Mundo, iniciar_mapa
from sistemas import itens, personagem, salvar, ui
from sistemas.combate import combate, duelo, tela_vitoria


def combate_treino(tela, jogador):
    """Luta aleatória fora do mapa."""
    inimigo = inimigo_aleatorio(jogador["nivel"])
    resultado = combate(tela, jogador, inimigo)
    if resultado == "vitoria":
        tela_vitoria(tela, jogador, inimigo)
    elif resultado == "derrota":
        ui.mensagem(tela, "DERROTA", [personagem.desmaiar(jogador)], cor_titulo=ui.VERMELHO)
    else:
        ui.mensagem(tela, "FUGA", ["Você fugiu da batalha."])


def iniciar_duelo(tela, jogador):
    """Duelo amistoso entre dois jogadores no mesmo teclado."""
    ui.mensagem(tela, "DUELO ENTRE PERSONAGENS", [
        "O Jogador 2 cria um personagem com o mesmo nível e os mesmos equipamentos do Jogador 1.",
        "Os dois jogam no mesmo teclado, um turno de cada vez.",
        "É um duelo amistoso: ninguém perde vida, itens ou XP.",
    ])
    nome = ui.entrada_texto(tela, "Jogador 2, digite o nome do seu personagem:", "Rival")
    rival = personagem.novo_personagem(nome, nivel=jogador["nivel"])
    rival["equipamento"] = dict(jogador["equipamento"])
    vencedor = duelo(tela, jogador, rival)
    ui.mensagem(tela, "FIM DO DUELO", [f'{vencedor["nome"]} venceu o duelo!'], cor_titulo=ui.OURO)


def menu(tela, jogador, mundo):
    opcoes = [
        "Explorar o mapa da floresta",
        "Ver ficha do personagem",
        "Inventário",
        "Bestiário de itens",
        "Ver fichas dos inimigos",
        "Combate de treino (aleatório)",
        "Duelo entre personagens (2 jogadores)",
        "Salvar jogo",
        "Sair do jogo",
    ]
    while True:
        escolha = ui.menu_vertical(tela, "CRÔNICAS DE UM REINO", opcoes, subtitulo=f'{jogador["nome"]}  |  Nível {jogador["nivel"]}',
                                   permitir_esc=False)
        if escolha == 0:
            iniciar_mapa(tela, jogador, mundo)
        elif escolha == 1:
            personagem.tela_ficha(tela, jogador)
        elif escolha == 2:
            itens.tela_inventario(tela, jogador)
        elif escolha == 3:
            itens.tela_catalogo(tela, jogador)
        elif escolha == 4:
            tela_bestiario(tela)
        elif escolha == 5:
            combate_treino(tela, jogador)
        elif escolha == 6:
            iniciar_duelo(tela, jogador)
        elif escolha == 7:
            ok = salvar.salvar(jogador)
            ui.mensagem(tela, "SALVAR JOGO", ["Jogo salvo com sucesso!" if ok else
                                              "Não foi possível salvar. Veja o arquivo erro.log."],
                        cor_titulo=ui.VERDE if ok else ui.VERMELHO)
        else:
            salvar.salvar(jogador)
            break
        salvar.salvar(jogador)


def escolher_jogador(tela):
    """Continua o jogo salvo ou começa um novo personagem."""
    if salvar.existe():
        salvo = salvar.carregar()
        if salvo is not None:
            escolha = ui.menu_vertical(
                tela, "CRÔNICAS DE UM REINO",
                [f'Continuar: {salvo["nome"]} (Nível {salvo["nivel"]})', "Novo jogo"],
                subtitulo="Um novo jogo guarda o save anterior em savegame.bak", permitir_esc=False)
            if escolha == 0:
                return salvo
    nome = ui.entrada_texto(tela, "Digite o nome do seu personagem:", "Aventureiro")
    jogador = personagem.novo_personagem(nome)
    salvar.salvar(jogador)
    return jogador


def main():
    pygame.init()
    pygame.display.set_caption("Crônicas de um Reino")
    tela = pygame.display.set_mode((ui.LARGURA, ui.ALTURA))
    jogador = escolher_jogador(tela)
    mundo = Mundo()
    try:
        menu(tela, jogador, mundo)
    except SystemExit:
        salvar.salvar(jogador)      # fechar a janela também salva
        raise
    except Exception:
        # qualquer erro inesperado: salva o progresso e anota o problema antes de fechar
        salvar.salvar(jogador)
        salvar.registrar_erro("Erro inesperado durante o jogo")
        pygame.quit()
        raise
    pygame.quit()


if __name__ == "__main__":
    main()
