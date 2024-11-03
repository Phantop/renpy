#!/usr/bin/env python3
from sys import argv
from ripgrepy import Ripgrepy
from re import compile as re
from pprint import pp as pprint


class Character:
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.kwargs = kwargs

    def speak(self, txt: str):
        print(f"{self.name}: {txt}")


class Game:
    def __init__(self, dir: str):
        self.dir = dir
        self.characters: dict[str, Character] = {}

        self.build_labels()
        self.build_init()

    def rg(self, x: str) -> dict:
        return Ripgrepy(x, self.dir).glob('*.rpy').json().run().as_dict

    def search(self, regex: str, keep: str = None):
        matches = self.rg(regex)
        if keep:
            output = {}
        else:
            output = []
        for i in matches:
            if i['type'] == 'match':
                match = i['data']['lines']['text']
                path = i['data']['path']['text']
                line = i['data']['line_number']
                loc = {'file': path, 'line': line}
                if keep:
                    name = re(keep).search(match).group(1)
                    output[name] = loc
                else:
                    output.append(loc)
        return output

    def build_labels(self):
        self.labels = self.search('^ *label .?*:', '^ *label (.*?):')
        pprint(self.labels)

    def build_init(self):
        self.init = self.search('^init:')
        pprint(self.init)


if __name__ == '__main__':
    if len(argv) != 2:
        exit()

    game = Game(argv[1])
