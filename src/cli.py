import os
import sys
import re

import model
from tabulate import tabulate
import json


class Cli:
    def __init__(self):
        # messages
        with open(r'res\strings.json') as f:
            contents = json.load(f)
            self.welcome, self.error_codes, self.help_codes = contents['welcome'], contents['error_codes'], contents[
                'help']

        # misc
        self.model = model.Model()
        self.mod_context = []
        self.command = None

    def help(self):
        print("MARCHITECT\n")
        for h in self.help_codes:
            self.command_help(h)

    def command_help(self, command):
        header = self.help_codes[command]['header']
        format_ = self.help_codes[command]['format']
        example = self.help_codes[command]['example']
        desc = self.help_codes[command]['desc']

        print(header)
        print('Format:', format_)
        print('Example:', example)
        print(desc, end='\n\n')

    def list(self):
        if self.command == 'list help':
            self.command_help('list')
            return

        if not self.model.mods:
            print(self.error_codes['1'])
            return

        headers = ['Index', 'Mod', 'Description', 'Downloads']
        mods = []
        for index, mod in enumerate(self.model.mods):
            mods.append([index + 1, mod['name'], mod['summary'], mod['downloads']])

        # noinspection PyArgumentList
        print('\n' + tabulate(mods, headers=headers, tablefmt='fancy_grid', maxcolwidths=[None, None, 40, None]) + '\n')

    def clear(self):
        if self.command == 'clear help':
            self.command_help('clear')
            return

        os.system('cls')

    def state(self):
        if self.command == 'state help':
            self.command_help('state')
            return

        mod_loader, game_version = self.model.get_state()
        print('\nMod Loader =', mod_loader)
        print('Game Version =', game_version, '\n')

    def exit(self):
        if self.command == 'exit help':
            self.command_help('exit')
            return

        sys.exit()

    def reset(self):
        if self.command == 'reset help':
            self.command_help('reset')
            return

        self.model.reset()
        print('\nMarchitect has been reset to its defaults!\n')

    def set(self):
        if self.command == 'set help':
            self.command_help('set')
            return

        res = re.search(r'^set (mod_loader (?:forge|fabric)|game_version [\d.]+)$', self.command)
        if res is None:
            print(self.error_codes['2'])
            return

        option, val = res.group(1).split()

        if option == "mod_loader":
            self.model.set_mod_loader(val)
        else:
            self.model.set_game_version(val)

        print('\nYour options were updated successfully!\n')

    def search(self):
        if self.command == 'search help':
            self.command_help('search')
            return

        res = re.search(r"^search ([\w ',.]+$)", self.command)
        if res is None:
            print(self.error_codes['2'])
            return

        results = self.model.search_call(res.group(1))

        if not results:
            print("\nYour search did not return any results :(\n")
            return

        self.mod_context = results

        headers = ['Index', 'Mod', 'Description', 'Downloads']
        mods = []
        for index, mod in enumerate(self.mod_context):
            mods.append([index + 1, mod['name'], mod['summary'], mod['downloads']])

        # noinspection PyArgumentList
        print('\n' + tabulate(mods, headers=headers, tablefmt='fancy_grid', maxcolwidths=[None, None, 40, None]) + '\n')

    def add(self):
        if self.command == 'add help':
            self.command_help('add')
            return

        res = re.search(r'^add (\d+)$', self.command)
        if res is None:
            print(self.error_codes['2'])
            return

        index = res.group(1)

        if not self.mod_context:
            print(self.error_codes['4'])
            return

        if int(index) < 1 or int(index) > len(self.mod_context):
            print(self.error_codes['3'])
            return

        self.model.add_mod(self.mod_context[int(index) - 1])
        print('\nMod added successfully!\n')

    def remove(self):
        if self.command == 'remove help':
            self.command_help('remove')
            return

        res = re.search(r'^remove (\d+)$', self.command)

        if res is None:
            print(self.error_codes['2'])
            return

        index = res.group(1)

        if not self.model.mods:
            print(self.error_codes['1'])
            return

        if int(index) < 1 or int(index) > len(self.model.mods):
            print(self.error_codes['3'])
            return

        del self.model.mods[int(index) - 1]
        print('\nMod removed successfully!\n')

    def export(self):
        if self.command == 'export help':
            self.command_help('export')
            return

        res = re.search(r'^export "?([A-Z]:[\\|/](?:[\w_\-. ]+[\\|/])*)([\w_\-. ]+\.txt)"?$', self.command)
        if res is None:
            print(self.error_codes['2'])
            return

        if not os.path.exists(res.group(1)):
            print(self.error_codes['5'])
            return

        path = os.path.join(res.group(1), res.group(2))
        self.model.export_file(path)

        print(f'\nMods exported at {path} successfully!\n')

    def download(self):
        if self.command == 'download help':
            self.command_help('download')
            return

        res = re.search(r'^download "?([A-Z]:[\\|/](?:[\w_\-. ]+[\\|/])*[\w_\-. ]+\.txt)"? -o "?([A-Z]:[\\|/](?:['
                        r'\w_\-. ]+[\\|/])*[\w_\-. ]+)[\\|/]?"?$', self.command)

        if res is None:
            print(self.error_codes['2'])
            return

        if not os.path.exists(res.group(1)):
            print(self.error_codes['6'])
            return

        if not os.path.exists(res.group(2)):
            print(self.error_codes['5'])
            return

        self.model.download_mods(res.group(1), res.group(2))
        print(f'\nThe mods has been downloaded successfully and saved at {res.group(2)}!\n')

    def load(self):
        if self.command == 'load help':
            self.command_help('load')
            return

        res = re.search(r'^load "?([A-Z]:[\\|/](?:[\w_\-. ]+[\\|/])*[\w_\-. ]+\.txt)"?$', self.command)
        if res is None:
            print(self.error_codes['2'])
            return

        if not os.path.exists(res.group(1)):
            print(self.error_codes['6'])
            return

        path = res.group(1)
        self.model.load(path)

    def check_deps(self):
        if self.command == 'depchk help':
            self.command_help('depchk')
            return

        if not self.model.mods:
            print(self.error_codes['1'])
            return

        self.model.check_deps()
        print('\nAll dependencies resolved!\n')

    def run(self):
        # noinspection PyUnresolvedReferences
        command_list = {
            'help': self.help,
            'list': self.list,
            'clear': self.clear,
            'state': self.state,
            'exit': self.exit,
            'reset': self.reset,
            'set': self.set,
            'search': self.search,
            'add': self.add,
            'remove': self.remove,
            'export': self.export,
            'download': self.download,
            'load': self.load,
            'depchk': self.check_deps
        }

        print(self.welcome)

        while True:
            inp = input('>>> ')

            if inp == '':
                continue

            if inp.split()[0] in command_list.keys():
                self.command = inp
                command_list.get(self.command.split()[0])()


# entry point
if __name__ == '__main__':
    c = Cli()
    c.run()
