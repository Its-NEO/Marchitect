import ast
import itertools
import json
import os.path
import os.path as path
import shutil
import time
from threading import Thread

import requests
import key


class Model:
    def __init__(self):
        # mod list
        self.mods = []

        # mod options (all set to defaults)
        self._game_version = '1.12.2'
        self._mod_loader = 'forge'
        self._sort_field = 2
        self._sort_order = 'desc'

        # constants
        self._GAME_ID = 432
        self._BASE_URL = 'https://api.curseforge.com'
        self._HEADERS = {
            'Accept': 'application/json',
            'x-api-key': key.get_key()
        }

    def set_game_version(self, game_version):
        self._game_version = game_version

    def set_mod_loader(self, mod_loader):
        self._mod_loader = mod_loader

    def add_mod(self, mod_obj: dict):
        self.mods.append(mod_obj)

    def remove_mod(self, mod_obj: dict):
        self.mods.remove(mod_obj)

    def get_state(self):
        return self._mod_loader, self._game_version

    def reset(self):
        self.mods = []
        self.set_game_version('1.12.2')
        self.set_mod_loader('forge')

    def search_call(self,
                    search_filter: str,
                    ) -> list:

        """
        Searches a mod with all the given parameters
        :param search_filter:   Search term
        :return:                [{
                                    'logo': string,
                                    'slug': string,
                                    'name': string,
                                    'summary': string,
                                    'authors': [string],
                                    'downloads': int,
                                    'categories': [{
                                        'name': string,
                                        'icon_url': string
                                    }],
                                    'size': int,
                                    'files': [{
                                        'fingerprint': int,
                                        'file_name': string,
                                        'download_url': string
                                    }],
                                }]
        """

        mod_loader_enum = {
            'forge': 1,
            'fabric': 4
        }

        # Search call
        data = requests.get(self._BASE_URL + '/v1/mods/search', headers=self._HEADERS, params={
            'gameId': self._GAME_ID,
            'gameVersion': self._game_version,
            'searchFilter': search_filter,
            'sortField': self._sort_field,
            'sortOrder': self._sort_order,
            'modLoaderType': mod_loader_enum[self._mod_loader]
        }).json()['data']

        # manufacturing the result
        result = [{
            'mod_id': d['id'],
            'name': d['name'],
            'summary': d['summary'],
            'authors': [author['name'] for author in d['authors']],
            'downloads': d['downloadCount'],
            'categories': [c['name'] for c in d['categories']],
            'deps': d['latestFiles'][0]['dependencies'],
            'files': [{
                'file_name': f['filename'],
                'game_version': f['gameVersion'],
                'file_id': f['fileId'],
                'mod_loader': f['modLoader']
            } for f in d['latestFilesIndexes'] if self._game_version in f['gameVersion']],
            'usable': True if d['latestFilesIndexes'][0]['filename'].endswith('jar') else False
        } for d in data]

        # sorting with mods with user selected priority if both forge and fabric versions available on same mod
        for element in result:
            new_mods = []
            for i, e in enumerate(element['files']):
                if mod_loader_enum.get(self._mod_loader) == e['mod_loader']:
                    new_mods.append(e)
            element['files'] = new_mods.copy()

        # Removing all the mods with empty files and mod packs
        result = [res for res in result if res['files'] and res['usable']]

        return result

    def export_file(self, out_path):
        """
        Exports a Marchitect file with all the necessary info to download the mods
        :param out_path:        File path of the (to be)exported file
        :return:                Exit codes
        """

        # removing any duplicate mods before exporting
        new_mods = []
        for element in self.mods:
            if element['mod_id'] not in [file['mod_id'] for file in new_mods]:
                new_mods.append(element)
        self.mods = new_mods

        # writing each mod with a new line
        with open(out_path, 'w') as file:
            for elem in self.mods:
                file.write(str(elem) + '\n')
                file.flush()

        self.mods = []

    def download_mods(self, src_file, out_dir):
        """
        Download all the mods from a Marchitect file
        :param src_file:        Source of the Marchitect file
        :param out_dir:         A directory to populate with downloaded mods
        :return:                True if successful, False if not
        """

        print("Downloading:")
        # Formatting contents of the file to dict Format
        with open(src_file) as file:
            mod_list = file.readlines()
        mod_list = [ast.literal_eval(mod.strip()) for mod in mod_list]

        is_done = False

        def _animate(*mod_name):
            for c in itertools.cycle(['|', '/', '-', '\\']):
                if is_done:
                    break
                print(f'{mod_name[0]}...{c}', end='\r')
                time.sleep(0.1)

        # downloading the mods
        for mod in mod_list:
            is_done = False
            animation_thread = Thread(target=_animate, args=[mod["name"]])
            animation_thread.start()

            # extracting mod info [first file to be taken]
            mod_file = mod['files'][0]
            mod_id, filename, file_id = mod['mod_id'], mod_file['file_name'], mod_file['file_id']

            # skipping already existing mods
            if path.exists(path.join(out_dir, filename)):
                is_done = True
                animation_thread.join()
                print(f'{mod["name"]} - Skipped')
                continue

            # checking if file exists in cache and adding it from cache
            if path.exists(path.join('cache', filename)):
                shutil.copyfile(path.join('cache', filename), path.join(out_dir, filename))
                is_done = True
                animation_thread.join()
                print(f'{mod["name"]} - DONE')
                continue

            # decoding file url after getting it
            file_url = requests.get(self._BASE_URL + f'/v1/mods/{mod_id}/files/{file_id}/download-url',
                                    headers=self._HEADERS)
            if file_url.content == b'':
                is_done = True
                animation_thread.join()
                print(f'{mod["name"]} - ERROR')  # <- if no download url found
                continue

            file_url = ast.literal_eval(file_url.content.decode())['data']
            r = requests.get(file_url, stream=True)
            with open(path.join(out_dir, filename), 'wb') as file:
                for chunk in r.iter_content(1024):
                    file.write(chunk)

            # copying file to the cache
            shutil.copyfile(path.join(out_dir, filename), path.join('cache', filename))

            is_done = True
            animation_thread.join()
            print(f'{mod["name"]} - Done!')

    def load(self, src_path):
        self.mods = []

        with open(src_path) as file:
            content = file.readlines()

        for mod in content:
            self.mods.append(ast.literal_eval(mod.strip()))

    def check_deps(self):
        count = 0
        flag = True
        while flag:
            for mod in self.mods:
                if mod['deps']:
                    for dep in mod['deps']:
                        dep_data = requests.get(self._BASE_URL + f'/v1/mods/{dep["modId"]}', headers=self._HEADERS)

                        if dep_data == b'':
                            continue

                        dep_data = json.loads(dep_data.content.decode())['data']

                        # manufacturing the result
                        result = {
                            'mod_id': dep_data['id'],
                            'name': dep_data['name'],
                            'summary': dep_data['summary'],
                            'authors': [author['name'] for author in dep_data['authors']],
                            'downloads': dep_data['downloadCount'],
                            'categories': [c['name'] for c in dep_data['categories']],
                            'deps': dep_data['latestFiles'][0]['dependencies'],
                            'files': [{
                                'file_name': f['filename'],
                                'game_version': f['gameVersion'],
                                'file_id': f['fileId'],
                                'mod_loader': f['modLoader']
                            } for f in dep_data['latestFilesIndexes'] if self._game_version in f['gameVersion']],
                            'usable': True if dep_data['latestFilesIndexes'][0]['filename'].endswith('jar') else False
                        }

                        if result not in self.mods:
                            self.add_mod(result)
                            count += 1

            if count == 0:
                flag = False

            count = 0
