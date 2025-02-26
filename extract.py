import os
from tabela_mapeamento import TabelaMapeamento

# Caminho do arquivo DINO.exe
caminho_dino = "DINO.exe"

# Offsets
offset_inicio = 0x24C9BE
offset_fim = 0x2535C3

def extrair_texto():
    # Verifica se a pasta ORIGINAL existe, se não, cria
    if not os.path.exists("ORIGINAL"):
        os.makedirs("ORIGINAL")

    # Abre o arquivo DINO.exe e lê os dados no intervalo especificado
    with open(caminho_dino, "rb") as arquivo:
        arquivo.seek(offset_inicio)
        dados = arquivo.read(offset_fim - offset_inicio)

    # Traduz os dados usando a tabela de mapeamento
    texto_traduzido = ""
    for i in range(0, len(dados), 2):  # Lê de 2 em 2 bytes
        byte = dados[i:i+2].hex().upper()  # Converte para hexadecimal e formata
        if byte in TabelaMapeamento.tabela:
            texto_traduzido += TabelaMapeamento.tabela[byte]
        else:
            texto_traduzido += "?"  # Caractere desconhecido

    # Separa o texto em linhas a cada [END] e mantém o [END] no final de cada linha
    linhas = texto_traduzido.split("[END]")
    linhas = [linha.strip() + "[END]" for linha in linhas if linha.strip()]  # Remove espaços e adiciona [END] encostado

    # Salva o texto traduzido no arquivo de saída
    caminho_saida = os.path.join("ORIGINAL", "tradução.txt")
    with open(caminho_saida, "w", encoding="utf-8") as arquivo_saida:
        for linha in linhas:
            arquivo_saida.write(linha + "\n")

    print(f"Texto extraído e salvo em {caminho_saida}")