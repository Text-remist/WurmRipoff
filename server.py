import socket
import json
import threading
import random
# Example height map and tree map
def create_height_map(rows, cols, min_height=0, max_height=10):
    return [[random.randint(min_height, max_height) for _ in range(cols)] for _ in range(rows)]

def create_tree_map(rows, cols, tree_density=0.5):
    return [[random.random() < tree_density for _ in range(cols)] for _ in range(rows)]

def create_rock_map(rows, cols, rock_density=0.3):
    return [[random.random() < rock_density for _ in range(cols)] for _ in range(rows)]

# Generate maps
height_map = create_height_map(20, 3)
tree_map = create_tree_map(20, 3)
rock_map = create_rock_map(20, 3)
print(len(tree_map))
print(len(rock_map))
clients = []

def handle_client(conn):
    global height_map, tree_map

    # Send initial data
    data = json.dumps({'tree_map': tree_map, 'rock_map': rock_map})
    conn.sendall(data.encode('utf-8'))

    while True:
        try:
            update = conn.recv(2048)
            if not update:
                break
            update = json.loads(update.decode('utf-8'))
            process_update(update)
        except Exception as e:
            print(f"Error: {e}")
            break

    conn.close()
    clients.remove(conn)

def process_update(update):
    global height_map, tree_map

    if 'tree_chop' in update:
        x, y = update['tree_chop']
        tree_map[x][y] = False
        print("Tree Map Updated")
        print(tree_map)
        notify_clients()
    if 'rock_smash' in update:
        x, y = update['rock_smash']
        tree_map[x][y] = False
        print("Rock Map Updated")
        print(rock_map)
        notify_clients()

def notify_clients():
    data = json.dumps({'tree_map': tree_map})
    for client in clients:
        try:
            client.sendall(data.encode('utf-8'))
        except Exception as e:
            print(f"Notification error: {e}")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 5555))
    server.listen(5)

    print("Server started, waiting for clients...")

    while True:
        conn, addr = server.accept()
        clients.append(conn)
        client_thread = threading.Thread(target=handle_client, args=(conn,))
        client_thread.start()
        print(tree_map)

if __name__ == "__main__":
    start_server()
