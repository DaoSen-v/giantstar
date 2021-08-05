try:

    from gaintstar._locust import main_locusts

except ModuleNotFoundError:
    raise ModuleNotFoundError(
        """We provide a beautiful testing framework for our test platform that integrates the most popular executors.
        You can use "pip install gaintstar" to install it and have a good time"
        """
    )

import os
import sys

dir = os.path.abspath("..")
index = sys.argv.index('--uuid')
pid_dir = os.path.join(dir, "runPid")

if not os.path.exists(pid_dir):
    os.makedirs(pid_dir)

with open(pid_dir+f'/{sys.argv[index+1]}', 'w+') as f:
    pid = os.getpid()
    f.write(str(pid))

main_locusts()