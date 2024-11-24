import Pyro4
import threading

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class ClienteChat(object):
    def __init__(self, nome):
        self.nome = nome
        self.ativo = True
        self.clientes_conectados = []

    @Pyro4.expose
    def receber_mensagem(self, mensagem):
        """Recebe uma mensagem do servidor e a exibe."""
        print(f"\n{mensagem}")
        print("Digite sua mensagem (ou 'sair' para encerrar): ", end='', flush=True)

    @Pyro4.expose
    def receber_lista_clientes(self, lista_clientes):
        """Recebe a lista atualizada de clientes."""
        self.clientes_conectados = lista_clientes
        print("\nClientes conectados:", ", ".join(lista_clientes))
        print("Digite sua mensagem (ou 'sair' para encerrar): ", end='', flush=True)

    def enviar_mensagens(self, servidor):
        while self.ativo:
            try:
                mensagem = input("Digite sua mensagem (ou 'sair' para encerrar): ")
                if mensagem.lower() == 'sair':
                    self.ativo = False
                    print("Saindo do chat...")
                    break
                servidor.enviar_mensagem(self.nome, mensagem)
            except Exception as e:
                print(f"Erro ao enviar mensagem: {e}")
                self.ativo = False
                break

    def iniciar(self):
        try:
            # Conectando ao servidor
            # ns = Pyro4.locateNS(host="IP", port=9999)
            ns = Pyro4.locateNS()
            uri_servidor = ns.lookup("servidor.chat")
            servidor = Pyro4.Proxy(uri_servidor)

            # Configurando o daemon do cliente
            daemon = Pyro4.Daemon()
            uri_cliente = daemon.register(self)

            # Thread para o daemon
            daemon_thread = threading.Thread(target=daemon.requestLoop)
            daemon_thread.daemon = True
            daemon_thread.start()

            print("Conectando ao servidor...")
            servidor.registrar_cliente(self.nome, uri_cliente)
            print("Conectado com sucesso!")

            # Loop principal para enviar mensagens
            self.enviar_mensagens(servidor)

        except Exception as e:
            print(f"Erro ao iniciar cliente: {e}")
        finally:
            try:
                servidor.desregistrar_cliente(self.nome)
            except:
                pass
            daemon.shutdown()

if __name__ == "__main__":
    nome_usuario = input("Digite seu nome de usuário: ")
    cliente = ClienteChat(nome_usuario)
    cliente.iniciar()
