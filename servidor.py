import Pyro4

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")  # Garante uma única instância
class ServidorChat(object):
    def __init__(self):
        if not hasattr(self, 'clientes'):  # Verifica se já foi inicializado
            self.clientes = {}
            print("Servidor inicializado. Lista de clientes vazia.")

    def registrar_cliente(self, nome, uri):
        print(f"Tentativa de registro: {nome}, URI: {uri}")
        if nome in self.clientes:
            raise ValueError(f"O nome de usuário '{nome}' já está em uso.")
        
        # Adiciona o novo cliente ao dicionário
        self.clientes[nome] = uri
        print(f"Cliente {nome} registrado com sucesso.")
        print(f"Lista atual de clientes: {list(self.clientes.keys())}")
        
        # Envia mensagem de boas-vindas
        self.broadcast(f"{nome} entrou no chat.", None)
        
        # Atualiza a lista de clientes para todos
        self.atualizar_lista_clientes()

    def enviar_mensagem(self, nome, mensagem):
        if nome not in self.clientes:
            raise ValueError(f"Usuário '{nome}' não registrado.")
        
        mensagem_formatada = f"{nome}: {mensagem}"
        print(f"Mensagem recebida de {nome}: {mensagem}")
        self.broadcast(mensagem_formatada, nome)

    def broadcast(self, mensagem, nome_cliente_enviando=None):
        print(f"Iniciando broadcast: {mensagem}")
        print(f"De: {nome_cliente_enviando if nome_cliente_enviando else 'Servidor'}")
        print(f"Clientes atuais: {list(self.clientes.keys())}")
        
        clientes_para_remover = []
        
        for nome, uri in list(self.clientes.items()):
                try:
                    print(f"Tentando enviar para {nome}")
                    cliente = Pyro4.Proxy(uri)
                    cliente._pyroTimeout = 5
                    cliente.receber_mensagem(mensagem)
                    print(f"Mensagem enviada com sucesso para {nome}")
                except Exception as e:
                    print(f"Erro ao enviar para {nome}: {e}")
                    clientes_para_remover.append(nome)

        # Remove clientes desconectados
        for nome in clientes_para_remover:
            print(f"Removendo cliente desconectado: {nome}")
            del self.clientes[nome]
        
        # Se algum cliente foi removido, atualiza a lista para todos
        if clientes_para_remover:
            self.atualizar_lista_clientes()

    def atualizar_lista_clientes(self):
        """Envia a lista atualizada de clientes para todos."""
        lista_clientes = list(self.clientes.keys())
        print(f"Atualizando lista de clientes. Lista atual: {lista_clientes}")
        
        for nome, uri in list(self.clientes.items()):  # Usa list() para evitar modificação durante iteração
            try:
                cliente = Pyro4.Proxy(uri)
                cliente._pyroTimeout = 5
                cliente.receber_lista_clientes(lista_clientes)
                print(f"Lista atualizada enviada para {nome}")
            except Exception as e:
                print(f"Erro ao atualizar lista para {nome}: {e}")
                del self.clientes[nome]
                print(f"Cliente {nome} removido por erro de comunicação")

    def desregistrar_cliente(self, nome):
        """Remove um cliente do chat."""
        if nome in self.clientes:
            del self.clientes[nome]
            self.broadcast(f"{nome} saiu do chat.")
            self.atualizar_lista_clientes()

def main():
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    
    # Limpa registro anterior se existir
    try:
        ns.remove("servidor.chat")
    except:
        pass
    
    uri = daemon.register(ServidorChat)
    ns.register("servidor.chat", uri)
    print(f"Servidor iniciado em {uri}")
    daemon.requestLoop()

if __name__ == "__main__":
    main()
