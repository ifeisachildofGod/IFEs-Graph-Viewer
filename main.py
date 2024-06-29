
import sys
import json
import threading
import subprocess
import time
from settings import *
from string import digits
from secrets import choice

def main():
    random_file_name = ''.join([choice(digits) for _ in range(20)]) + '.json'
    
    with open(random_file_name, "w") as file:
        file.write(json.dumps(DEFAULT_API_STATE, indent=2))
    
    gc_thread = threading.Thread(target=lambda: subprocess.run(['py', 'run_app_components.py', 'GraphCalculator', str(random_file_name)]))
    gc_thread.daemon = True
    gc_thread.start()
    subprocess.run(['py', 'run_app_components.py', 'GraphApp', str(random_file_name)])

if __name__ == '__main__':
    main()
    sys.exit()


