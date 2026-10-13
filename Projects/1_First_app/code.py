import time
from datetime import datetime

def main():
    print("=== 24/7 Docker Container Test ===")
    print("Container started. Type 'quit' to exit.\n")
    
    counter = 0
    while True:
        try:
            user_input = input(f"[{datetime.now()}] Enter something (or 'quit'): ")
            
            if user_input.lower() == 'quit':
                print("Exiting...")
                break
            
            counter += 1
            print(f"Received #{counter}: {user_input}")
            print(f"Uptime: {time.time() - start_time:.2f} seconds\n")
            
        except EOFError:
            # Handle case where no stdin is available (running detached)
            print("No stdin available, sleeping...")
            time.sleep(60)
        except KeyboardInterrupt:
            print("\nInterrupted. Exiting...")
            break

if __name__ == "__main__":
    start_time = time.time()
    main()