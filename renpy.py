#!/usr/bin/env python3
import sys
from glob import glob
from pprint import pp
from ripgrepy import Ripgrepy as rg
pprint = pp


def _(a: str):
    '''Ignore gettext translations'''
    return a


class Character:
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.kwargs = kwargs

    def speak(self, txt: str):
        print(f"{self.name}: {txt}")


class Block:
    '''Denotes an indented block, in which all lines are > indent spaces in'''

    def __init__(self, indent: int):
        self.indent = indent


class Line:
    def __init__(self, line: str):
        self.indent = len(line) - len(line.lstrip())
        self.keyword = line.split()[0]
        self.arg_arr = line.split()[1:]
        self.arg_str = ' '.join(self.arg_arr)


class Game:
    def __init__(self, loc: str):
        self.dir = loc
        self.files = glob(f'{self.dir}/**/*.rpy', recursive=True)
        self.__preprocess()

    def __search(self, regex: str, keep: int = None):
        '''
        Search all scripts for a given pattern.
        Useful for items needed at game start.
        '''
        matches = rg(regex, self.dir).glob('*.rpy').json().run().as_dict
        matches = [m['data'] for m in matches if m['type'] == 'match']
        output = {} if keep else []
        for m in matches:
            file = m['path']['text']
            line = m['line_number']
            text = m['submatches'][0]['match']['text']
            loc = (file, line)
            if keep:
                name = text.split()[keep]
                output[name] = loc
            else:
                output.append(loc)
        return output

    def __preprocess(self):
        '''
        Load in data needed upon game load, before start.
        Includes: storing label and init locations, processing defines/defaults
        '''
        self.labels = self.__search('^ *label [^:]*', 1)
        self.init = self.__search('^init:')
        if self.init[0]:
            self.file = self.init[0][0]
            self.line = self.init[0][1]
        else:
            self.file = self.labels['start'][0]
            self.line = self.labels['start'][1]

        self.characters: dict[str, Character] = {}


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    game = Game(path)
