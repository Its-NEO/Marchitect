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
            header = self.help_codes[h]['header']
            format_ = self.help_codes[h]['format']
            example = self.help_codes[h]['example']
            desc = self.help_codes[h]['desc']

            print(header)
            print('Format:', format_)
            print('Example:', example)
            print(desc, end='\n\n')

    def list(self):
        if self.command == 'list help':
            header = self.help_codes['list']['header']
            format_ = self.help_codes['list']['format']
            example = self.help_codes['list']['example']
            desc = self.help_codes['list']['desc']

            print(header)
            print('Format:', format_)
            print('Example:', example)
            print(desc, end='\n\n')
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
            header = self.help_codes['clear']['header']
            format_ = self.help_codes['clear']['format']
            example = self.help_codes['clear']['example']
            desc = self.help_codes['clear']['desc']

            print(header)
            print('Format:', format_)
            print('Example:', example)
            print(desc, end='\n\n')
            return

        os.system('cls')

    def state(self):
        if self.command == 'state help':
            header = self.help_codes['state']['header']
            format_ = self.help_codes['state']['format']
            example = self.help_codes['state']['example']
            desc = self.help_codes['state']['desc']

            print(header)
            print('Format:', format_)
            print('Example:', example)
            print(desc, end='\n\n')
            return

        mod_loader, game_version = self.model.get_state()
        print('\nMod Loader =', mod_loader)
        print('Game Version =', game_version, '\n')

    def exit(self):
        if self.command == 'exit help':
            header = self.help_codes['exit']['header']
            format_ = self.help_codes['exit']['format']
            example = self.help_codes['exit']['example']
            desc = self.help_codes['exit']['desc']

            print(header)
            print('Format:', format_)
            print('Example:', example)
            print(desc, end='\n\n')
            return

        sys.exit()

    def reset(self):
        if self.command == 'reset help':
            header = self.help_codes['reset']['header']
            format_ = self.help_codes['reset']['format']
            example = self.help_codes['reset']['example']
            desc = self.help_codes['reset']['desc']

            print(header)
            print('Format:', format_)
            print('Example:', example)
            print(desc, end='\n\n')
            return

        self.model.reset()
        print('\nMarchitect has been reset to its defaults!\n')

    def set(self):
        if self.command == 'set help':
            header = self.help_codes['set']['header']
            format_ = self.help_codes['set']['format']
            example = self.help_codes['set']['example']
            desc = self.help_codes['set']['desc']

            print(header)
            print('Format:', format_)
            print('Example:', example)
            print(desc, end='\n\n')
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
            header = self.help_codes['search']['header']
            format_ = self.help_codes['search']['format']
            example = self.help_codes['search']['example']
            desc = self.help_codes['search']['desc']

            print(header)
            print('Format:', format_)
            print('Example:', example)
            print(desc, end='\n\n')
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
            header = self.help_codes['add']['header']
            format_ = self.help_codes['add']['format']
            example = self.help_codes['add']['example']
            desc = self.help_codes['add']['desc']

            print(header)
            print('Format:', format_)
            print('Example:', example)
            print(desc, end='\n\n')
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
            header = self.help_codes['remove']['header']
            format_ = self.help_codes['remove']['format']
            example = self.help_codes['remove']['example']
            desc = self.help_codes['remove']['desc']

            print(header)
            print('Format:', format_)
            print('Example:', example)
            print(desc, end='\n\n')
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
            header = self.help_codes['export']['header']
            format_ = self.help_codes['export']['format']
            example = self.help_codes['export']['example']
            desc = self.help_codes['export']['desc']

            print(header)
            print('Format:', format_)
            print('Example:', example)
            print(desc, end='\n\n')
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
            header = self.help_codes['download']['header']
            format_ = self.help_codes['download']['format']
            example = self.help_codes['download']['example']
            desc = self.help_codes['download']['desc']

            print(header)
            print('Format:', format_)
            print('Example:', example)
            print(desc, end='\n\n')
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
            header = self.help_codes['load']['header']
            format_ = self.help_codes['load']['format']
            example = self.help_codes['load']['example']
            desc = self.help_codes['load']['desc']

            print(header)
            print('Format:', format_)
            print('Example:', example)
            print(desc, end='\n\n')
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
            header = self.help_codes['depchk']['header']
            format_ = self.help_codes['depchk']['format']
            example = self.help_codes['depchk']['example']
            desc = self.help_codes['depchk']['desc']

            print(header)
            print('Format:', format_)
            print('Example:', example)
            print(desc, end='\n\n')
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
