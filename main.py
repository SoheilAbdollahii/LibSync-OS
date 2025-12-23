import threading
import time
import random

# --- 1. Voroodiha ---
print("--- Tanzimat-e Proje ---")
num_readers = int(input("Tedad Reader-ha ra vared konid: "))
num_borrowers = int(input("Tedad Borrower-ha ra vared konid: "))
queue_limit = int(input("Zarfiat safe darkhast: "))
initial_books = int(input("Tedad ketabhaye mojood dar database: "))

# --- 2. Manabe Moshtarak ---
db_content = {"books_count": initial_books}
request_queue = [] 
read_count = 0

# --- 3. Abzarhaye Synchronization (Locks & Semaphores) ---
database_access = threading.Lock() 
read_count_lock = threading.Lock() 
queue_lock = threading.Lock()      

queue_capacity = threading.Semaphore(queue_limit) 
requests_available = threading.Semaphore(0)       

# --- 4. Tab-e Reader ---
def reader_thread(r_id):
    global read_count
    while True:
        time.sleep(random.uniform(3, 10))
        
        with read_count_lock:
            read_count += 1
            if read_count == 1:
                print(f" [Reader {r_id}] Avalin nafar ast va montazer-e ghofl-e database mimanad...")
                database_access.acquire()
            print(f" [Reader {r_id}] Shorooh be khandan kard. [Active Readers: {read_count}]")
        
        time.sleep(random.uniform(1, 3)) 
        
        with read_count_lock:
            read_count -= 1
            print(f" [Reader {r_id}] Motale'e tamam shod. [Active Readers: {read_count}]")
            if read_count == 0:
                print(" Akharin nafar kharej shod. Ghofl-e database azad shod.")
                database_access.release()

# --- 5. Tab-e Borrower ---
def borrower_thread(b_id):
    while True:
        time.sleep(random.uniform(1, 4))
        print(f" [Borrower {b_id}] Mikhad darkhast-e amanat bede...")
        
        queue_capacity.acquire()
        
        with queue_lock:
            request_queue.append(b_id)
            print(f" [Borrower {b_id}] Darkhast sabt shod. [Size-e saf: {len(request_queue)}]")
        
        requests_available.release() 

# --- 6. Tab-e Librarian ---
def librarian_thread():
    while True:
        print(" [Librarian] Montazer-e darkhast mimanad...")
        requests_available.acquire() 
        
        with queue_lock:
            borrower_id = request_queue.pop(0)
            print(f" [Librarian] Darkhast-e borrower {borrower_id} ra bardasht. [Size-e saf: {len(request_queue)}]")
        
       
        queue_capacity.release()
        
        print(f" [Librarian] Montazer-e ghofl-e database baraye borrower {borrower_id}...")
        database_access.acquire()
        
        print(f" [Librarian] (Writer) Vared-e database shod baraye borrower {borrower_id}.")
        if db_content["books_count"] > 0:
            db_content["books_count"] -= 1
            time.sleep(1) 
            print(f" Ketab be borrower {borrower_id} dade shod. [Mojoodi: {db_content['books_count']}]")
        else:
            print(f" Ketabi baraye borrower {borrower_id} mojood nist!")
            
        database_access.release()
        print(f" [Librarian] (Writer) Az database kharej shod.")

# --- 7. Ejraye Threads ---
print("\n--- Simulation Shorooh Shod ---")

t_lib = threading.Thread(target=librarian_thread, daemon=True)
t_lib.start()

for i in range(num_readers):
    threading.Thread(target=reader_thread, args=(i+1,), daemon=True).start()

for i in range(num_borrowers):
    threading.Thread(target=borrower_thread, args=(i+1,), daemon=True).start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nShutting down the simulation...")