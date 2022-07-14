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
            self.error_codes, self.help_codes = contents['error_codes'], contents['help']

        # misc
        self.model = model.Model()
        self.mod_context = []
        self.command = None

    def help(self):
        pass

    def list(self):
        if not self.model.mods:
            print(self.error_codes['1'])
            return

        headers = ['Index', 'Mod', 'Description', 'Downloads']
        mods = []
        for index, mod in enumerate(self.model.mods):
            mods.append([index + 1, mod['name'], mod['summary'], mod['downloads']])

        # noinspection PyArgumentList
        print('\n' + tabulate(mods, headers=headers, tablefmt='fancy_grid', maxcolwidths=[None, None, 40, None]) + '\n')

    @staticmethod
    def clear():
        os.system('cls')

    def state(self):
        mod_loader, game_version = self.model.get_state()
        print('\nMod Loader =', mod_loader)
        print('Game Version =', game_version, '\n')

    @staticmethod
    def exit():
        sys.exit()

    def reset(self):
        self.model.reset()
        print('\nMarchitect has been reset to its defaults!\n')

    def set(self):
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
        res = re.search(r'^add (\d)$', self.command)
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
        res = re.search(r'^remove (\d)$', self.command)

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
            'download': self.download
        }

        print()

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
