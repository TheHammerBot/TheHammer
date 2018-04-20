"""
    The Hammer
    Copyright (C) 2018 JustMaffie

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import time
import threading

# Made by Jacob Wiltse <https://github.com/Kelwing>
class TimerResetDict(threading.Thread):

    pure_dict = dict()

    def __setitem__(self, key, item):
        x = True
        while x:
            try:
                self.pure_dict[key] = item
                x = False
            except RuntimeError:
                pass

    def __getitem__(self, key):
        x = True
        while x:
            try:
                return self.pure_dict[key]
                x = False
            except RuntimeError:
                pass

    def __repr__(self):
        return repr(self.pure_dict)

    def __len__(self):
        return len(self.pure_dict)

    def __delitem__(self, key):
        x = True
        while x:
            try:
                del self.pure_dict[key]
                x = False
            except RuntimeError:
                pass

    def clear(self):
        return self.pure_dict.clear()

    def copy(self):
        return self.pure_dict.copy()

    def has_key(self, k):
        return k in self.pure_dict

    def update(self, *args, **kwargs):
        return self.pure_dict.update(*args, **kwargs)

    def keys(self):
        return self.pure_dict.keys()

    def values(self):
        return self.pure_dict.values()

    def items(self):
        return self.pure_dict.items()

    def pop(self, *args):
        return self.pure_dict.pop(*args)

    def __cmp__(self, dict_):
        return self.__cmp__(self.pure_dict, dict_)

    def __contains__(self, item):
        return item in self.pure_dict

    def __iter__(self):
        return iter(self.pure_dict)

    def run(self):
        while True:
            time.sleep(self.seconds)
            self.pure_dict = dict()

    def __init__(self, seconds):
        super().__init__()
        self.daemon = True
        self.seconds = seconds
        self.start()