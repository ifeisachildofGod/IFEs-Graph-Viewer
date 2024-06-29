
import subprocess
import sys
import json
import threading
from settings import *
from misc_components import APIObject
from graph import GraphApp
from calculator import GraphCalculator

api_file = sys.argv[2]

func_texts = []

def make_graph_calculator_thread():
    gc_thread = threading.Thread(target=lambda: subprocess.run(['py', 'run_app_components.py', 'GraphCalculator', api_file]))
    gc_thread.daemon = True
    gc_thread.start()

api = APIObject(api_file)

if sys.argv[1] == 'GraphCalculator':
    def send_function(text: str, color: ColorType, index: int):
        info = text, color
        api_info = api.read_from_api()
        if index < len(api_info[FUNC_INFO_ID]):
            api_info[FUNC_INFO_ID][index] = info
        else:
            api_info[FUNC_INFO_ID].append(info)
        
        api.write_to_api(api_info)

    def remove_function(index: int):
        api_info = api.read_from_api()
        if index < len(api_info[FUNC_INFO_ID]):
            api_info[FUNC_INFO_ID].pop(index)
            api.write_to_api(api_info)
    
    GraphCalculator(api_file, send_function, remove_function).run()

elif sys.argv[1] == 'GraphApp':
    GraphApp(api_file, make_graph_calculator_thread).run()

