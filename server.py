import socket
import pickle
import threading
from time import sleep
from gamestate import GameState

class Server:
    def __init__(self, port = 5566, size = 4096, max_connection = 1) -> None:
        self.ip = "172.16.15.75"
        self.port = port
        self.addr = (self.ip, self.port)
        self.size = size
        self.format = "utf-8"
        self.server_id = (f"[Server {socket.gethostname()} ({self.ip}:{self.port})]")
        self.max_connection = max_connection
        
        self.clients = []
        self.clients_lock = threading.Lock()

    def broadcast_message(self, message):
        for client in self.clients:
            try:
                if isinstance(message, str):
                    data = message.encode(self.format)
                else:
                    data = pickle.dumps(message)
                client["connection"].sendall(data)
            except Exception as e:
                print(f"[ERROR] {e}")

    def handle_client(self, conn, addr):
        
        CLIENT_ID = (f"[Client ({addr[0]} @ {addr[1]})]")
        print(f"{CLIENT_ID}  Estabilished connection to server.")
        
        connected = True
        while connected:
            try:
                recv_data_binary = conn.recv(self.size)
            except ConnectionResetError:
                print(f"[{addr[0]}] Disconnected")
                break
            except Exception as e:
                print(f"[ERROR] {e}")
                break
            
            try:
                recv_data = recv_data_binary.decode()
            except UnicodeDecodeError:
                recv_data = pickle.loads(recv_data_binary)
            except Exception as e:
                print(f"[ERROR] {e}")
                break
            
            print(f"[{addr[0]}] {recv_data}")
            self.broadcast_message(recv_data)

                
        with self.clients_lock:
            self.clients[:] = [client for client in self.clients if client["address"] != addr]

        try:
            conn.close()
        except Exception as e:
            print(f"[ERROR] {e}")
            
    def start(self):
        print(f"{self.server_id} Server is starting...")
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind(self.addr)
            server.listen(self.max_connection)
        except:
            print(f"{self.server_id} Server failed to start. Port {self.port} is currently in use by another process.")
            return
        print(f"{self.server_id} Server is listening on {self.ip}:{self.port}")

        while len(self.clients) < self.max_connection:
            conn, addr = server.accept()
            client_info = {"connection": conn, "address": addr}
            with self.clients_lock:
                self.clients.append(client_info)
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.start()  
        
    # sleep(2)
    
    # print(f"{SERVER_ID} [GAME] All players have connected to the server")
    # print(f"{SERVER_ID} [GAME] Game is starting...")
    # print(f"{SERVER_ID} [GAME] Players: {game.get_player_names_str()}")
    # broadcast_message("GSET:1")

# if __name__ == "__main__":
x = Server()
x.start()
input("Enter to start")
x.broadcast_message("among us")
x.broadcast_message("sus")
x.broadcast_message("verb")
x.broadcast_message("tae")
x.broadcast_message("random")
