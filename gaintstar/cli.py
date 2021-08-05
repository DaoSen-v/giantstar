from gaintstar.testFactory import TestFactory
from gaintstar import __description__, __version__

import sys
import argparse
from argparse import Namespace

from gaintstar.utils.scaffold import command_parser_scaffold, main_scaffold


def command_parser_run(subparsers):
    sub_parser_run = subparsers.add_parser('run', help="Make gaintstar testcase and run with runner.")
    sub_parser_run.add_argument(
        '-r',
        '--runner',
        default='pytest',
        choices=['pytest', 'nosetest', 'unittest', 'behavior', 'locust'],
        help='添加一个执行器'
    )
    sub_parser_run.add_argument('-u', '--url', help='远程下载测试计划入口\neg. https://flybear.cass.time')
    sub_parser_run.add_argument('-c','--config', help='远程下载项目配置入口\neg. https://flybear.cass.time')
    sub_parser_run.add_argument('-a','--args', help="执行器命令行参数\n eg.'--alluredir=./report, -s, -p, no:warning'")
    sub_parser_run.add_argument('-i', '--uuid', help='执行程序时的进程号名称')
    return sub_parser_run
#
#
def main_run(args: Namespace):
    command = []
    if args.args:
        command = args.args.replace(" ", "").split(',')
    TestFactory.run(command_args=command, runner_name=args.runner, kwargs=args)


def main():
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument(
        "-V", "--version", dest="version", action="store_true", help="show version"  
    )
    subparsers = parser.add_subparsers(help="sub-command help")
    sub_parser_run = command_parser_run(subparsers)
    sub_parser_make = command_parser_scaffold(subparsers)
    args = parser.parse_args()
    sys_args = sys.argv

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    elif len(sys_args) == 2:
        if sys.argv[1] in ["-V", "--version"]:
            print(f"{__version__}")
        elif sys.argv[1] == "run":
            sub_parser_run.print_help()
        elif sys.argv[1] in ["-h", "--help"]:
            parser.print_help()
        elif sys.argv[1] == "startproject":
            sub_parser_make.print_help()
        sys.exit(0)

    if sys_args[1] == "run":
        main_run(args)
    elif sys_args[1] == "startproject":
        main_scaffold(args)

if __name__ == '__main__':
    main()