from extract import extrair_texto
from insert import inserir_texto_e_ponteiros

def menu():
    while True:
        print("\nEscolha uma opção:")
        print("1 - Extrair texto")
        print("2 - Inserir texto e ponteiros")
        print("3 - Sair")
        opcao = input("Opção: ")

        if opcao == "1":
            extrair_texto()
        elif opcao == "2":
            inserir_texto_e_ponteiros()
        elif opcao == "3":
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    menu()