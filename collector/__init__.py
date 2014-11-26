import sys
from logging import (info as _info,
                     error as _error,
                     warning as _warn,
                     debug as _debug,
                     getLogger,
                     INFO,
                     StreamHandler,
                     Formatter)

root = getLogger()
root.setLevel(INFO)
ch = StreamHandler(sys.stdout)
ch.setLevel(INFO)
formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)