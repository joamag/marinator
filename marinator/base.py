#!/usr/bin/python
# -*- coding: utf-8 -*-

import time

import appier
import appier_console

import ripe

MESSAGE = """To Marina and the QA team and all the other members that sacrifice their time in tasks necessary and that require resilience, you represent the heart and soul of PlatformE.
Marina two words for you: You rock 🤘"""

class Marinator(object):

    def run(self):
        with appier_console.ctx_loader(template = "{{spinner}} Processing 3 seconds"):
            time.sleep(3)

        print(MESSAGE)

if __name__ == "__main__":
    marinator = Marinator()
    marinator.run()
else:
    __path__ = []
