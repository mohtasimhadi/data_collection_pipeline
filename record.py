import argparse
from utils.logs import *
from modules.recording import start_recording

functions = {
    'record'        : (start_recording, ['out_dir'])
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Data Collection Pipeline for DepthAI")
    parser.add_argument('--o', choices=functions.keys(), help=f'Function to call. Select from {functions.keys()}')

    for param_name in set(param_name for func, param_names in functions.values() for param_name in param_names):
        parser.add_argument(f'--{param_name}', help=f'Parameter {param_name}')

    args = parser.parse_args()
    
    if args.o is None or args.o ==  '':
        print(f"{ERROR}No operation is selected! \n{LOG}Try running: {GREEN} python main.py{RESET} --o <operation name>\n{LOG}Valid operations are {YELLOW}{', '.join(map(str, functions.keys()))}{RESET}")
        print(f"{LOG}For help, run: {GREEN} python main.py{RESET} -h")
        exit()

    func, param_names = functions[args.o]

    func_args = []
    for param_name in param_names:
        param_value = getattr(args, param_name)
        if param_value is not None:
            func_args.append(param_value)
    
    func(*func_args)