import Pyro4

# Classe do Servidor de Chat
@Pyro4.expose
class ServidorChat:
    def __init__(self):
        self.clientes = {}

    def registrar_cliente(self, nome, uri):
        print(f"Tentativa de registro: {nome}, URI: {uri}")
        if nome in self.clientes:
            raise ValueError(f"O nome de usuário '{nome}' já está em uso.")
        self.clientes[nome] = uri
        print(f"Cliente {nome} registrado com sucesso. Enviando broadcast...")
        try:
            # Envia a lista de clientes conectados para o novo cliente
            self.enviar_lista_clientes(uri)
            self.broadcast(f"{nome} entrou no chat.")
        except Exception as e:
            print(f"Erro ao enviar broadcast: {e}")
        print("Registro de cliente finalizado.")

    def enviar_mensagem(self, nome, mensagem):
        """Recebe uma mensagem de um cliente e a distribui para todos os outros."""
        if nome not in self.clientes:
            raise ValueError(f"Usuário '{nome}' não registrado.")
        
        mensagem_formatada = f"{nome}: {mensagem}"  # Formatação da mensagem
        print(f"Mensagem recebida de {nome}: {mensagem_formatada}")
        self.broadcast(mensagem_formatada, nome)  # Envia para todos os clientes, exceto o que enviou
        print(f"Mensagem enviada: {mensagem_formatada}")

    def broadcast(self, mensagem, nome_cliente_enviando=None):
        """Envia uma mensagem para todos os clientes registrados, exceto o cliente que enviou."""
        clientes_para_remover = []
        for nome, uri in self.clientes.items():
            try:
                # Não envia para o cliente que enviou a mensagem
                if nome != nome_cliente_enviando:
                    cliente = Pyro4.Proxy(uri)
                    cliente.receber_mensagem(mensagem)  # Envia a mensagem para o cliente
            except Exception as e:
                print(f"Erro ao enviar mensagem para {nome}: {e}")
                clientes_para_remover.append(nome)
        
        # Remove clientes desconectados
        for nome in clientes_para_remover:
            print(f"Removendo cliente desconectado: {nome}")
            del self.clientes[nome]

    def enviar_lista_clientes(self, uri_novo_cliente):
        """Envia a lista de clientes conectados para o novo cliente."""
        lista_clientes = list(self.clientes.keys())  # Obtemos apenas os nomes
        try:
            cliente = Pyro4.Proxy(uri_novo_cliente)
            cliente.receber_lista_clientes(lista_clientes)
        except Exception as e:
            print(f"Erro ao enviar lista de clientes: {e}")

# Inicialização do servidor
def main():
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS(host="localhost") 
    uri = daemon.register(ServidorChat)
    ns.register("servidor.chat", uri)
    print("Servidor de chat iniciado.")
    daemon.requestLoop()    

if __name__ == "__main__":
    main()
