import Pyro4
import threading

class ClienteChat:
    def __init__(self, nome):
        self.nome = nome
        self.ativo = True  # Variável para controlar o loop principal

    @Pyro4.expose
    def receber_mensagem(self, mensagem):
        """Recebe uma mensagem do servidor e a exibe."""
        print(f"Mensagem recebida: {mensagem}")  # Exibe a mensagem recebida de outros usuários

    def enviar_mensagens(self, servidor):
        """Loop para enviar mensagens ao servidor."""
        while self.ativo:
            try:
                mensagem = input("Digite sua mensagem (ou 'sair' para encerrar): ")
                if mensagem.lower() == "sair":
                    self.ativo = False
                    print("Saindo do chat...")
                    break
                # Exibe a própria mensagem antes de enviá-la
                print(f"Você: {mensagem}")
                servidor.enviar_mensagem(self.nome, mensagem)  # Envia para o servidor
            except Exception as e:
                print(f"Erro ao enviar mensagem: {e}")
                break

    def mostrar_clientes_conectados(self, servidor):
        """Solicita a lista de clientes conectados e a exibe."""
        try:
            clientes = servidor.obter_clientes_conectados()  # Solicita os clientes conectados ao servidor
            print("\nClientes conectados:")
            for cliente in clientes:
                print(f"- {cliente}")
        except Exception as e:
            print(f"Erro ao obter clientes conectados: {e}")

    def iniciar(self):
        """Conecta ao servidor e inicia o cliente."""
        try:
            # Conectando ao servidor
            print("Localizando o servidor...")
            ns = Pyro4.locateNS()  # Localiza o nameserver
            uri_servidor = ns.lookup("servidor.chat")  # Obtém o URI do servidor
            servidor = Pyro4.Proxy(uri_servidor)  # Cria um proxy para o servidor

            # Configura o daemon para o cliente
            print("Configurando o daemon do cliente...")
            daemon = Pyro4.Daemon()
            uri_cliente = daemon.register(self)  # Registra o cliente no daemon

            # Thread para o daemon
            daemon_thread = threading.Thread(target=daemon.requestLoop, daemon=True)
            daemon_thread.start()
            print("Daemon do cliente iniciado e pronto para receber mensagens.")

            # Agora que o cliente está pronto, registramos no servidor
            print("Tentando registrar cliente no servidor...")
            servidor.registrar_cliente(self.nome, uri_cliente)
            print("Cliente registrado no servidor com sucesso.")

            # Exibir clientes conectados após o registro
            self.mostrar_clientes_conectados(servidor)

            # Loop para enviar mensagens
            self.enviar_mensagens(servidor)

        except Exception as e:
            print(f"Erro: {e}")

if __name__ == "__main__":
    nome_usuario = input("Digite seu nome de usuário: ")
    cliente = ClienteChat(nome_usuario)
    cliente.iniciar()
