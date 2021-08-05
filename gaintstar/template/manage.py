import os
import sys
from gaintstar.utils.logger import logger

dir = os.path.abspath("..")
index = sys.argv.index('--uuid')
pid_dir = os.path.join(dir, "runPid")
if not os.path.exists(pid_dir): os.makedirs(pid_dir)

with open(pid_dir+f'/{sys.argv[index+1]}', 'w+') as f:
    pid = os.getpid()
    f.write(str(pid))

logger.info(f'【生成进程信息】文件路径={pid_dir}, 文件名={sys.argv[index+1]}，进程={pid}')

try:
    from gaintstar.cli import main

    main()
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        """We provide a beautiful testing framework for our test platform that integrates the most popular executors.
        You can use "pip install gaintstar" to install it and have a good time"
        """
    )


