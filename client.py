import random
import socket
import json
import threading
import time

class Client:
    def __init__(self, server_ip):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((server_ip, 5555))
        self.tree_map = None
        self.rock_map = None
        self.lock = threading.Lock()
        self.start()

    def start(self):
        # Receive initial data
        data = self.client.recv(2048)
        maps = json.loads(data.decode('utf-8'))
        print("Initial tree map:", maps['tree_map'])
        print("Initial rock map:", maps['rock_map'])
        self.tree_map = maps['tree_map']
        self.rock_map = maps['rock_map']
        # Start a thread to listen for updates from the server
        threading.Thread(target=self.listen_for_updates).start()

        # Start a thread to simulate changes in data
        threading.Thread(target=self.simulate_changes).start()

    def listen_for_updates(self):
        while True:
            update = self.client.recv(2048)
            if not update:
                break
            maps = json.loads(update.decode('utf-8'))
            with self.lock:
                if 'tree_map' in maps:
                    self.tree_map = maps['tree_map']
                    print("Updated tree map:", self.tree_map)
                if 'rock_map' in maps:
                    self.rock_map = maps['rock_map']
                    print("Updated rock map:", self.rock_map)

    def simulate_changes(self):
        while True:
            time.sleep(5)  # Wait for 5 seconds before chopping another tree
            self.chop_tree(random.randint(0,19), random.randint(0,2))
            self.smash_rock(random.randint(0,19), random.randint(0,2))

    def chop_tree(self, x, y):
        with self.lock:
            if self.tree_map[x][y]:
                self.tree_map[x][y] = False
                update = json.dumps({'tree_chop': [x, y]})
                self.client.sendall(update.encode('utf-8'))
                print(f"Chopped tree at ({x}, {y})")

    def smash_rock(self, x, y):
        with self.lock:
            if self.tree_map[x][y]:
                self.tree_map[x][y] = False
                update = json.dumps({'rock_smash': [x, y]})
                self.client.sendall(update.encode('utf-8'))
                print(f"Smashed Rock at ({x}, {y})")
if __name__ == "__main__":
    server_ip = 'localhost'  # Replace with the actual server IP if needed
    Client(server_ip)
