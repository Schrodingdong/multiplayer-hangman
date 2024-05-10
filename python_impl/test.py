import threading
import time

# Function that will be executed by the first thread
def thread_one(event, data):
    print("Thread One: Waiting for data...")
    event.wait()  # Wait until the event is set
    print("Thread One: Data received:", data[0])

# Function that will be executed by the second thread
def thread_two(event, data):
    time.sleep(3)  # Simulate some work before sending data
    data[0] = "Hello from Thread Two!"
    event.set()  # Set the event to notify Thread One

# Creating an event object
event = threading.Event()

# Some shared data between threads
shared_data = [None]

# Creating the threads
t1 = threading.Thread(target=thread_one, args=(event, shared_data))
t2 = threading.Thread(target=thread_two, args=(event, shared_data))

# Starting the threads
t1.start()
t2.start()

# Waiting for both threads to finish
t1.join()
t2.join()

print("Main Thread: Both threads have finished.")

