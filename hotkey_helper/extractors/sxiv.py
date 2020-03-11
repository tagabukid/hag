import os
import re

from pathlib import Path

from .base import Extractor
from .base import File
from .base import Command
from .base import Manpage


class Sxiv(Extractor):
    required = [Command('sxiv')]
    sources = {'default': [Manpage('sxiv')],
               'key_handler': [File(Path(os.environ['XDG_CONFIG_HOME']) / 'sxiv' / 'exec' / 'key-handler')]}
    has_modes = True

    @staticmethod
    def _clean_action(string):
        return string.replace('\n', ' ').strip()

    @staticmethod
    def _clean_key(string):
        return string.replace('\-', '-').strip()

    def _extract(self):
        content = self.fetched['default'][0]
        # to selection sectio from manpage
        content_section = re.compile(r'\.SH KEYBOARD COMMANDS.*?\.SH', re.DOTALL)
        # to split the section in different mode
        content_modes = re.compile(r'\.SS\s(.*?\n)(.*?)(?=(\.SS)|$)', re.DOTALL)
        # get each key/action from the mode section
        mode_key_action = re.compile(r'\.B[R]?\s(.*?\n)(.*?)(=?\.TP\n)', re.DOTALL)
        # clean up some stray strings
        content_clean = re.compile(r'(", ")|(\.I[R]? )')
        # only keep the desired man page section
        content = re.search(content_section, content)[0]
        # clean
        content = re.sub(content_clean, '', content)
        # find all the modes
        modes_content = re.finditer(content_modes, content)
        out = {}
        for mode_content in modes_content:
            mode = mode_content[1].rstrip()
            mode_c = mode_content[2]
            # add mode
            if mode not in out.keys():
                out[mode] = {}
            # find all the key/actions
            for key_action in re.finditer(mode_key_action, mode_c):
                key = self._clean_key(key_action[1])
                action = self._clean_action(key_action[2])
                out[mode][key] = action

        # extract key_handler
        if self.fetched['key_handler']:
            out['key-handler'] = {}
            content = self.fetched['key_handler'][0]
            # remove comments
            comments = re.compile(r'\s*#.*')
            # get key/action
            content_cases = re.compile(r"\s\"(.*)\"\)\s*\n\s*(.*(?=;;))")
            # clean
            content = re.sub(comments, '', content)
            cases = re.finditer(content_cases, content)
            for case in cases:
                key = case[1]
                action = case[2]
                out['key-handler'][key] = action
        return out

