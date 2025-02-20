import os
import struct

# Função para carregar a tabela de mapeamento a partir do arquivo .tbl
def carregar_tabela(caminho_tabela):
    tabela = {}
    with open(caminho_tabela, 'r', encoding='utf-8') as file:
        for linha in file:
            linha = linha.strip()  # Remove espaços em branco e quebras de linha
            if linha and '=' in linha:  # Verifica se a linha não está vazia e contém '='
                hex_valor, char = linha.split('=', 1)  # Divide a linha no primeiro '='
                # Se o valor após o '=' estiver vazio, considera como espaço
                if char.strip() == '':
                    char = ' '
                tabela[hex_valor.upper()] = char  # Adiciona ao dicionário
    return tabela

# Função para converter hexadecimal para texto legível
def hex_para_texto(hex_str, tabela):
    texto = ''
    # Divide a string hexadecimal em partes de 4 caracteres (cada valor hexadecimal)
    for i in range(0, len(hex_str), 4):
        hex_valor = hex_str[i:i+4]
        if hex_valor in tabela:
            texto += tabela[hex_valor]
        else:
            texto += '?'  # Caractere desconhecido
    return texto

# Função para extrair o texto do arquivo binário
def extrair_texto(arquivo_binario, caminho_tabela, arquivo_txt, offset_inicial, offset_final):
    try:
        # Carregar a tabela de mapeamento
        tabela = carregar_tabela(caminho_tabela)

        # Abrir o arquivo binário no modo de leitura binária
        with open(arquivo_binario, 'rb') as file:
            # Pular para o offset inicial
            file.seek(offset_inicial)
            # Ler o intervalo de bytes desejado
            tamanho_bytes = offset_final - offset_inicial
            dados_hex = file.read(tamanho_bytes).hex().upper()  # Converte para hexadecimal

        # Converter o hexadecimal para texto legível
        texto_legivel = hex_para_texto(dados_hex, tabela)

        # Salvar o texto legível em um arquivo TXT na pasta Original
        caminho_original = os.path.join('Original', arquivo_txt)
        with open(caminho_original, 'w', encoding='utf-8') as file:
            file.write(texto_legivel)

        print(f"Texto extraído salvo em '{caminho_original}'")

    except FileNotFoundError as e:
        print(f"Arquivo não encontrado: {e}")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

# Função para converter texto legível para hexadecimal
def texto_para_hex(texto, tabela):
    hex_str = ''
    i = 0
    while i < len(texto):
        # Verifica se o próximo caractere é um caractere especial (como [LN] ou [END])
        if texto[i] == '[':
            # Encontra o fechamento do caractere especial
            fim = texto.find(']', i)
            if fim == -1:
                raise ValueError(f"Caractere especial malformado: {texto[i:]}")
            # Extrai o caractere especial (por exemplo, [LN] ou [END])
            char_especial = texto[i:fim+1]
            # Procura o caractere especial na tabela de mapeamento
            if char_especial in tabela.values():
                # Encontra o valor hexadecimal correspondente
                hex_valor = next(k for k, v in tabela.items() if v == char_especial)
                hex_str += hex_valor
            else:
                # Se não encontrar, substitui por '0000'
                hex_str += '0000'
            i = fim + 1
        else:
            # Mapeia caracteres normais
            char = texto[i]
            if char in tabela.values():
                hex_valor = next(k for k, v in tabela.items() if v == char)
                hex_str += hex_valor
            else:
                hex_str += '0000'  # Caractere desconhecido (substitui por 0000)
            i += 1
    return hex_str

# Função para ler os ponteiros originais do arquivo binário
def ler_ponteiros_originais(arquivo_binario, offset_ponteiro_inicial, num_ponteiros):
    ponteiros = []
    with open(arquivo_binario, 'rb') as file:
        file.seek(offset_ponteiro_inicial)
        for _ in range(num_ponteiros):
            ponteiro = struct.unpack('<I', file.read(4))[0]
            ponteiros.append(ponteiro)
    return ponteiros

# Função para calcular os novos ponteiros a partir do texto editado
def calcular_novos_ponteiros(texto_editado, ponteiros_originais, indice_inicio_edicao):
    blocos = texto_editado.split('[END]')
    blocos = [bloco.strip() for bloco in blocos if bloco.strip()]  # Remove blocos vazios

    # Ajustar os ponteiros a partir do índice de início da edição
    for i in range(indice_inicio_edicao, len(blocos)):
        if i == 0:
            ponteiros_originais[i] = 1  # O primeiro ponteiro sempre começa com 1
        else:
            # O ponteiro atual é o ponteiro anterior + o tamanho do bloco anterior + 1 (para o [END])
            ponteiros_originais[i] = ponteiros_originais[i - 1] + len(blocos[i - 1]) + 1

    return ponteiros_originais

# Função para inserir o texto editado e atualizar os ponteiros (se necessário)
def inserir_texto_com_ponteiros(arquivo_binario, caminho_tabela, arquivo_txt, offset_inicial, offset_final, offset_ponteiro_inicial):
    try:
        # Carregar a tabela de mapeamento
        tabela = carregar_tabela(caminho_tabela)

        # Ler o arquivo TXT editado da pasta Editada
        caminho_editado = os.path.join('Editada', arquivo_txt)
        with open(caminho_editado, 'r', encoding='utf-8') as file:
            texto_editado = file.read()

        # Ler o arquivo TXT original da pasta Original
        caminho_original = os.path.join('Original', arquivo_txt)
        with open(caminho_original, 'r', encoding='utf-8') as file:
            texto_original = file.read()

        # Verificar se o texto foi realmente editado
        if texto_editado == texto_original:
            print("O texto não foi editado. Nenhuma alteração será feita.")
            return

        # Encontrar o índice onde a edição começa
        indice_inicio_edicao = 0
        for i in range(min(len(texto_editado), len(texto_original))):
            if texto_editado[i] != texto_original[i]:
                indice_inicio_edicao = texto_original[:i].count('[END]')
                break

        # Ler os ponteiros originais
        num_ponteiros = texto_original.count('[END]')
        ponteiros_originais = ler_ponteiros_originais(arquivo_binario, offset_ponteiro_inicial, num_ponteiros)

        # Calcular os novos ponteiros a partir do índice de início da edição
        novos_ponteiros = calcular_novos_ponteiros(texto_editado, ponteiros_originais, indice_inicio_edicao)

        # Converter o texto editado para hexadecimal
        hex_str = texto_para_hex(texto_editado, tabela)
        tamanho_editado = len(hex_str) // 2  # Cada byte é representado por 2 caracteres hex

        # Verificar se o texto editado ultrapassa o limite final
        if offset_inicial + tamanho_editado > offset_final:
            excedente = (offset_inicial + tamanho_editado) - offset_final
            print(f"ERRO: O texto editado ultrapassa o limite final em {excedente} bytes.")
            return

        # Exibir o tamanho original e o tamanho atual
        tamanho_original = offset_final - offset_inicial
        print(f"Tamanho original do texto: {tamanho_original} bytes")
        print(f"Tamanho atual do texto editado: {tamanho_editado} bytes")

        # Abrir o arquivo binário no modo de leitura/escrita binária
        with open(arquivo_binario, 'r+b') as file:
            # Atualizar os ponteiros
            offset_ponteiro_atual = offset_ponteiro_inicial
            for ponteiro in novos_ponteiros:
                file.seek(offset_ponteiro_atual)
                # Escrever o ponteiro como um número de 32 bits em little-endian
                file.write(struct.pack('<I', ponteiro))
                offset_ponteiro_atual += 4  # Cada ponteiro ocupa 4 bytes

            # Escrever o texto editado no offset inicial
            file.seek(offset_inicial)
            file.write(bytes.fromhex(hex_str))

        print(f"Texto editado e ponteiros atualizados com sucesso!")

    except FileNotFoundError as e:
        print(f"Arquivo não encontrado: {e}")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

# Função principal com menu
def main():
    # Caminho do arquivo binário de entrada/saída
    arquivo_binario = 'DINO.exe'
    # Caminho do arquivo TXT editado
    arquivo_txt = 'texto_convertido.txt'
    # Caminho do arquivo de tabela (.tbl)
    caminho_tabela = 'dino1.tbl'

    # Offsets (em hexadecimal)
    offset_inicial = 0x24C9BE  # Offset onde o texto começa
    offset_final = 0x2535C8    # Limite final do bloco de texto
    offset_ponteiro_inicial = 0x24C28C  # Offset do primeiro ponteiro

    while True:
        print("\nMenu:")
        print("1 - Extrair texto")
        print("2 - Inserir texto editado e atualizar ponteiros")
        print("3 - Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            print("\nExtraindo texto...")
            extrair_texto(arquivo_binario, caminho_tabela, arquivo_txt, offset_inicial, offset_final)
        elif opcao == '2':
            print("\nInserindo texto editado e atualizando ponteiros...")
            inserir_texto_com_ponteiros(arquivo_binario, caminho_tabela, arquivo_txt, offset_inicial, offset_final, offset_ponteiro_inicial)
        elif opcao == '3':
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")

# Executar a função principal
if __name__ == "__main__":
    main()