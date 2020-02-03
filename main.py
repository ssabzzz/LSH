import sys
from LSH import LSH
import yaml
import time

if __name__ == '__main__':
    #
    config = {}
    t0 = time.time()
    assert len(sys.argv) == 2 , "\n You may run the program using command: 'python main.py [config_file address] '"
    with open(sys.argv[1], 'r') as stream:
        try:
           config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    my_instance = LSH(config)
    t1 = time.time()
    print("It took {} seconds to run the program.".format(t1-t0))
    
    