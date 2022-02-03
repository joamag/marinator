#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import json
import time
import uuid

import appier
import appier_console

import ripe

MESSAGE = """To Marina and the QA team and all the other members that sacrifice their time in tasks necessary and that require resilience, you represent the heart and soul of PlatformE.
Marina two words for you: You rock 🤘"""

class Marinator(object):

    def run(self, path = "downloads"):
        config = self.load_config()

        if not os.path.exists(path):
            os.makedirs(path)

        base_url = config.get("base_url", "https://ripe-core-sbx.platforme.com/api/")
        token = config.get("token", "")

        with appier_console.ctx_loader(template = "{{spinner}} Loading") as thread:
            thread.template = "{{spinner}} Logging in to RIPE instance"
            ripe_api = ripe.API(base_url = base_url)
            ripe_api.login_pid(token)

            thread.template = "{{spinner}} Running a small sleep"
            time.sleep(0)

            try:
                thread.template = "{{spinner}} Creating orders..."
                for model in config["models"]:
                    # tries to obtain the name of the color for the
                    # base part that is going to be use in the improt
                    color = model.rsplit("v", 1)[1]
                    parts = dict(
                        body = dict(
                            material = "silk",
                            color = color
                        ),
                        shadow = dict(
                            material = "default",
                            color = "default"
                        )
                    )

                    contents = dict(
                        brand = config["brand"],
                        model = model,
                        parts = parts,
                        size = config.get("size", 17)
                    )

                    # creates the order according to the provided brand
                    # and model parts structure
                    order = ripe_api.import_order(
                        ff_order_id = str(uuid.uuid4()),
                        contents = json.dumps(contents)
                    )

                    order_report = ripe_api.report_pdf(order["number"])

                    print(order_report)

            except Exception as exception:
                import pprint
                if hasattr(exception, "read"):
                    pprint.pprint(json.loads(exception.read()))
                else:
                    print(exception)

        print(MESSAGE)

    def load_config(self, filename = "config.json", encoding = "utf-8"):
        """
        Loads the configuration using the name of the file provided
        as parameter, assumes that the structure is JSON compatible.

        :type filename: String
        :param filename: The name of the file that is going to be loaded
        as the configuration one.
        :type encoding: String
        :param encoding: The name of the encoding to be used to decode
        the contents of the JSON file.
        :rtype: Dictionary
        :return: The final configuration loaded from the provided filename.
        """

        file = open(filename, "rb")
        try: data = file.read()
        finally: file.close()
        data = data.decode(encoding)
        data_j = json.loads(data)
        return data_j

if __name__ == "__main__":
    marinator = Marinator()
    marinator.run()
else:
    __path__ = []
