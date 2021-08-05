import os.path
import shutil
import subprocess
import sys

from gaintstar.utils.logger import logger


def command_parser_scaffold(subparsers):
    sub_parser_scaffold = subparsers.add_parser(
        "startproject", help="Create a new project with template structure."
    )
    sub_parser_scaffold.add_argument(
        "project_name", type=str, nargs="?", help="Specify new project name."
    )
    return sub_parser_scaffold


def create_scaffold(project_name):
    """ create scaffold with specified project name.
    """
    def show_tree(prj_name):
        try:
            print(f"\n$ tree {prj_name} -a")
            subprocess.run(["tree", prj_name, "-a"])
            print("")
        except FileNotFoundError:
            logger.warning("tree command not exists, ignore.")

    if os.path.isdir(project_name):
        logger.warning(
            f"Project folder {project_name} exists, please specify a new project name."
        )
        show_tree(project_name)
        return 1
    elif os.path.isfile(project_name):
        logger.warning(
            f"Project name {project_name} conflicts with existed file, please specify a new one."
        )
        return 1

    logger.info(f"Create new project: {project_name}")
    logger.info(f"Project Root Dir: {os.path.join(os.getcwd(), project_name)}")
    new_project_dir = os.path.join(os.getcwd(), project_name)
    from_path = os.path.dirname(os.path.dirname(__file__)) + '/template'

    os.mkdir(new_project_dir)
    copy_file(from_path, new_project_dir)
    logger.info(f"Create new project success···")
    return 0


def copy_file(from_path, target_path):
    file_list = os.listdir(from_path)
    for file in file_list:
        file_path = os.path.join(from_path, file)
        if os.path.isfile(file_path):
            new_file_path = os.path.join(target_path, file)
            shutil.copyfile(file_path, new_file_path)
        elif os.path.isdir(file_path):
            new_target = os.path.join(target_path, file)
            os.makedirs(new_target)
            copy_file(file_path, new_target)


def main_scaffold(args):
    # capture_message("startproject with scaffold")
    sys.exit(create_scaffold(args.project_name))
