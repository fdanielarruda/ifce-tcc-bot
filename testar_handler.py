from services.transacao_service import TransacaoService


def main_teste_interativo():
    print("🤖 Iniciando Testador Interativo de Handler.")
    print("💬 Digite a mensagem que você quer enviar para o handler.")
    print("🛑 Digite 'sair' ou pressione Ctrl+C para encerrar.")
    print("--------------------------------------------------")

    while True:
        try:
            mensagem_digitada = input(">> Digite sua mensagem: ")

            if mensagem_digitada.lower() in ['sair', 'exit', 'parar']:
                break

            transacao_service = TransacaoService()
            mensagem = transacao_service.processar_mensagem(mensagem_digitada, "123456")
            print(mensagem)

        except KeyboardInterrupt:
            break
        except EOFError:
            break
        except Exception as e:
            print(f"❌ Erro inesperado no loop principal: {e}")
            break

    print("\n👋 Testes finalizados!")


if __name__ == "__main__":
    main_teste_interativo()