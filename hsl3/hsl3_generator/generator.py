__version__ = '0.3.0'
__author__ = 'Martin Welgraven'

import os
import re
import sys
import argparse


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from hsl3.hsl3_generator.configs.dcls_project import ConfigProject
from hsl3.hsl3_generator.configs.dcls_module import ConfigModule
from hsl3.hsl3_generator.parsers.python import PythonfileParser
from hsl3.hsl3_generator.parsers.json import JSONfileParser
from hsl3.hsl3_generator.parsers.tests import TestfileParser


def setup():
    parser = argparse.ArgumentParser(description=f'Generator (v{__version__}) for the generation of HSL3 logic blocks.')
    
    parser.add_argument('-i', '--init', action='store_true', help='Initialize a new project and create a basic json configuration file')
    parser.add_argument('-c', '--create', action='store_true', help='Creates the python file based on the json configuration. Existing code will be overwritten.')
    parser.add_argument('-b', '--build', action='store_true', help='Builds the project to a HSL file and generate the HTML documentation')
    
    args = parser.parse_args()

    if args.init == True:
        return 'init'
    elif args.create == True:
        return 'create'
    elif args.build == True:
        return 'build'
    else:
        msg = ("No valid action provided. Please use:\n"
               " • '-i' or '--init' to initalise the project, \n"
               " • '-c' or '--create' to create the base python file\n"
               " • '-b' or '--build' to build the project.")
        print(msg)
        return


def load_project() -> tuple[ConfigProject, ConfigModule]:
    project = ConfigProject(ROOT_DIR)
    config_file = ""
    for dirpath, dirnames, filenames in os.walk(project.source_path):
        for filename in filenames:
            if filename.endswith('.json'):
                config_file = filename
                break

    node = JSONfileParser().parse_json(os.path.join(project.source_path, config_file))
    if node is None:
        print("No valid JSON configuration found. Please run the generator with the '-i' or '--init' flag to create a new project.")
        exit()
    
    return (project, node)


def project_init():
    logic_id = input("Enter the project id (format: '12345'):")
    while not re.fullmatch(r'^[0-9]{5}$', logic_id):
        logic_id = input("Invalid format | Enter the project id (format: '12345'):")
    
    logic_name = input("Enter the project name (format: 'my-project-name'):").lower()
    while not re.fullmatch(r'^[a-z]+(?:-[a-z0-9]+)*$', logic_name):
        logic_name = input("Invalid format |Enter the project name (format: 'my-project-name'):").lower()

    category = input("In which category should the logic node be listed [IOT Device Data]:") or "IOT Device Data"
    while not re.fullmatch(r'^[A-Za-z0-9]+(?:\s&\s[A-Za-z0-9]+)*(?:\-[A-Za-z0-9]+)*$', category):
        category = input("Invalid format |Enter the category (format: 'IOT Device & Data01'):") or "IOT Device Data"

    context = input(f"In what context should the logic node run [{logic_name.replace('-','_')}]:") or logic_name.replace('-','_')
    while not re.fullmatch(r'^[a-z]+(?:_[a-z0-9]+)*$', context):
        context = input("Invalid format |Enter the context (format: 'my_project_name'):").lower() or logic_name.replace('-','_')
    
    project = ConfigProject(ROOT_DIR, logic_id, logic_name)
    if project.json_exists():
        overwrite = ""
        while overwrite.lower() not in ['y', 'n']:
            overwrite = input("The JSON file already exists and will be overwritten. Do you want to continue 'Y' or 'N'?:")
        if overwrite.lower() == "n":
            return

    JSONfileParser().write_first_json(project, category, context)
    print("Project initialization complete, src folder, tests folder and JSON configuration file created.")


def python_base_file(project: ConfigProject, node: ConfigModule):
    if project.python_exists():
        overwrite = ""
        while overwrite.lower() not in ['y', 'n']:
            overwrite = input("The Python file already exists and will be overwritten. Do you want to continue 'Y' or 'N'?:")
        if overwrite.lower() == "n":
            return
    
    PythonfileParser().write_first_python(project.python_path(), node)


def build_hsl(project: ConfigProject, node: ConfigModule):
    msg = "Would you like to create the HSL file? 'Y' or 'N'?:"
    if project.hsl_exists():
        msg = "The HSL file already exists and will be overwritten. Do you want to continue 'Y' or 'N'?:"
    
    continue_build = ""
    while continue_build.lower() not in ['y', 'n']:
        continue_build = input(msg)
        msg = "Invalid input | " + msg if msg[:len("Invalid input")] != "Invalid input" else msg

    if continue_build.lower() == "n":
        return

    # TODO: implement HSL file generation

def build_html(project: ConfigProject, node: ConfigModule):
    msg = "Would you like to create the HTML file? 'Y' or 'N'?:"
    if project.html_exists():
        msg = "The HTML file already exists and will be overwritten. Do you want to continue 'Y' or 'N'?:"
    
    continue_build = ""
    while continue_build.lower() not in ['y', 'n']:
        continue_build = input(msg)
        msg = "Invalid input | " + msg if msg[:len("Invalid input")] != "Invalid input" else msg

    if continue_build.lower() == "n":
        return
    
    # TODO: implement HTML file generation

def build_tests(project: ConfigProject, node: ConfigModule):
    msg = "Would you like to create the tests file? 'Y' or 'N'?:"
    if project.testfile_exists():
        msg = "The tests file already exists and will be overwritten. Do you want to continue 'Y' or 'N'?:"
    
    continue_build = ""
    while continue_build.lower() not in ['y', 'n']:
        continue_build = input(msg)
        msg = "Invalid input | " + msg if msg[:len("Invalid input")] != "Invalid input" else msg

    if continue_build.lower() == "n":
        return
    
    TestfileParser(project.testfile_path(), project.json_file, node)

        
def main():
    action = setup()
    
    if action=='init':
        project_init()
    
    else:
        project, node = load_project()
        project.id = node.id
        project.name = node.name

        if action == 'create':
            python_base_file(project, node)
        elif action == 'build':
            build_hsl(project, node)
            build_html(project, node)
            build_tests(project, node)
        else:
            print("No valid action provided.")

if __name__ == '__main__':
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f'\nCreating HSL3 Logic Block\n=========================\n')
    main()
    print(f'\n===========END===========\n')