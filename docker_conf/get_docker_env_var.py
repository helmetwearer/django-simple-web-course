import os, pathlib, sys

curr_path = pathlib.Path(__file__).parent.resolve()

with open(os.path.join(curr_path, 'envvariables.bak')) as file:
    for line in file:
        if '=' in line:
            parts = line.rstrip().split('=')
            if parts[0].upper() == sys.argv[1]:
                print(parts[1])
                break