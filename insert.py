import os
from tabela_mapeamento import TabelaMapeamento

# Caminho do arquivo tradução.txt
caminho_tradução = os.path.join("EDITADA", "tradução.txt")

# Offsets
offset_texto_inicio = 0x24C9BE  # Início do texto no DINO.exe
offset_ponteiros_inicio = 0x24C28C  # Início dos ponteiros no DINO.exe
offset_ponteiros_fim = 0x24C9B8  # Fim dos ponteiros no DINO.exe

def inserir_texto_e_ponteiros():
    # Verifica se o arquivo tradução.txt existe na pasta EDITADA
    if not os.path.exists(caminho_tradução):
        print(f"Arquivo {caminho_tradução} não encontrado.")
        return

    # Lê o conteúdo do arquivo tradução.txt
    with open(caminho_tradução, "r", encoding="utf-8") as arquivo:
        texto = arquivo.read()

    # Remove quebras de linha e espaços extras
    texto = texto.replace("\n", "").strip()

    # Divide o texto em blocos separados por [END]
    blocos = texto.split("[END]")
    blocos = [bloco.strip() for bloco in blocos if bloco.strip()]

    # Verifica se há blocos suficientes
    if len(blocos) < 1:
        print("Erro: O arquivo tradução.txt não contém blocos suficientes para calcular os ponteiros.")
        return

    # Inicializa o primeiro ponteiro
    ponteiro_atual = 0x0001  # 1 em hexadecimal
    offset_atual = offset_ponteiros_inicio

    # Abre o arquivo DINO.exe para escrita
    with open("DINO.exe", "r+b") as arquivo:
        # Insere o texto no DINO.exe
        arquivo.seek(offset_texto_inicio)
        texto_bytes = b""
        for bloco in blocos:
            # Converte o texto para bytes usando a tabela de mapeamento
            for char in bloco:
                # Procura o caractere na tabela de mapeamento
                byte = None
                for key, value in TabelaMapeamento.tabela.items():
                    if value == char:
                        byte = bytes.fromhex(key)
                        break
                if byte:
                    texto_bytes += byte
                else:
                    print(f"Erro: Caractere '{char}' não encontrado na tabela de mapeamento.")
                    return

            # Adiciona o [END] ao final de cada bloco (exceto o último)
            if bloco != blocos[-1]:
                texto_bytes += bytes.fromhex("00A0")  # [END]

        # Escreve o texto no DINO.exe
        arquivo.write(texto_bytes)

        # Insere os ponteiros no DINO.exe
        arquivo.seek(offset_ponteiros_inicio)
        for i, bloco in enumerate(blocos):
            # Calcula o número de caracteres no bloco atual
            caracteres_bloco = len(bloco.replace("[LN]", " "))  # Substitui [LN] por um espaço para contagem correta

            # Adiciona 1 para o [END] (exceto no último bloco)
            if i < len(blocos) - 1:
                caracteres_bloco += 1

            # Converte o ponteiro para little-endian
            ponteiro_bytes = ponteiro_atual.to_bytes(2, byteorder="little")

            # Insere o ponteiro no offset atual
            arquivo.seek(offset_atual)
            arquivo.write(ponteiro_bytes)

            # Exibe o ponteiro inserido
            print(f"Offset {hex(offset_atual)}: {ponteiro_bytes.hex()[:2]}x{ponteiro_bytes.hex()[2:]}")

            # Avança para o próximo offset (4 bytes por ponteiro)
            offset_atual += 4

            # Calcula o próximo ponteiro
            ponteiro_atual += caracteres_bloco

            # Verifica se o ponteiro ultrapassou 0xFF00
            if ponteiro_atual > 0xFF00:
                ponteiro_atual = 0x0101  # Reinicia a contagem

            # Verifica se atingimos o offset final
            if offset_atual > offset_ponteiros_fim:
                print("Atenção: Todos os offsets disponíveis foram preenchidos.")
                break

    print("Texto e ponteiros inseridos com sucesso no arquivo DINO.exe.")