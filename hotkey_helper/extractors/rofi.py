import re

from .base import Extractor
from .base import CommandCheck
from .base import CommandFetch


class Rofi(CommandFetch, CommandCheck, Extractor):
    cmd = 'rofi'
    fetch_cmd = 'rofi -dump-config'
    has_modes = False

    @staticmethod
    def _clean_key(string):
        string = string.lstrip()[1:-1]
        return string

    def _extract(self):
        line_match = re.compile(r'(/\*)?\t((kb)|(me)|(ml))')
        line_clean = re.compile(r'((/\*)|(\*/)|(\t)|(;))')
        out = {}
        for line in self.fetched.split('\n'):
            if re.match(line_match, line):
                line = re.sub(line_clean, '', line)
                line_split = line.split(':')
                key = self._clean_key(line_split[1])
                action = line_split[0]
                out[key] = action
        return out

