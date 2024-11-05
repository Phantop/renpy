#!/usr/bin/env python3
import sys
from dataclasses import dataclass
from pprint import pp
from ripgrepy import Ripgrepy as rg
pprint = pp

def _(a: str):
    '''Ignore gettext translations'''
    return a


@dataclass
class Loc:
    file: str
    line: int
    indent: int


class Character:
    def __init__(self, name: str, **kwargs):
        self.name = name

    def speak(self, txt: str):
        print(f"{self.name}: {txt}")


class Line:
    def __init__(self, line: str):
        self.indent = len(line) - len(line.lstrip())
        line = line.strip()
        self.blank = len(line) == 0
        if self.blank:
            self.keyword = ''
            self.arg = []
        elif line.startswith('"'):
            self.keyword = '"'
            self.arg = line[1:].split()
        else:
            self.keyword = line.split()[0]
            self.arg = line.split()[1:]
        self.args = ' '.join(self.arg)

    def __getitem__(self, indices):
        if isinstance(indices, tuple):
            return ' '.join(self.arg[indices])
        return ''.join(self.arg[indices])


class Game:
    '''
    Implements core logic for initialization and execution of the game
    '''

    def __init__(self, d: str):
        self.dir = d
        self.variables = {}
        self.__commands()
        self.__preprocess()

    def __commands(self):
        '''
        Set up dict of interpreter commands
        '''
        self.commands: dict = {
            '$': self.__assignment,
            'menu:': self.__menu,
        }

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
            indent = Line(m['lines']['text']).indent
            loc = Loc(file, line, indent)
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
        self.labels: dict[str, Loc] = self.__search('^ *label [^:]*', 1)
        self.init: list[Loc] = self.__search('^init:')

        self.stack: list[Loc] = []
        for loc in self.init:
            self.run(loc)

    def run(self, loc: Loc):
        self.stack.append(loc)
        with open(self.stack[-1].file, encoding='utf-8') as f:
            # jump to desired line of file:
            zip(range(self.stack[-1].line), next(f))
            for line in f:
                self.stack[-1].line += 1
                line = Line(line)
                if line.keyword in self.commands:
                    self.commands[line.keyword](line)
                if line.indent <= self.stack[-1].indent:
                    break

    def __assignment(self, line: Line):
        match line[1]:
            case '=':
                self.variables[line[0]] = eval(line[2:])

    def __menu(self):
        raise NotImplementedError


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    game = Game(path)
