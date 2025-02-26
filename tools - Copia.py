import os

# Caminho do arquivo tradução.txt
caminho_tradução = os.path.join("EDITADA", "tradução.txt")

# Offsets dos ponteiros
offset_inicial = 0x24C28C
offset_final = 0x24C9B8

def calcular_ponteiros():
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
    offset_atual = offset_inicial

    # Abre o arquivo DINO.exe para escrita
    with open("DINO.exe", "r+b") as arquivo:
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
            if offset_atual > offset_final:
                print("Atenção: Todos os offsets disponíveis foram preenchidos.")
                break

if __name__ == "__main__":
    calcular_ponteiros()