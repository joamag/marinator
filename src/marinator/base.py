#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import json
import time
import uuid
import datetime
import itertools

import appier_console

import ripe

MESSAGE = """To Marina, the QA team and all the other members that sacrifice their time in tasks necessary and that require resilience, you represent the heart and soul of PlatformE.
Marina two words for you - You rock 🤘
This tool has been made with ❤️"""

class Marinator(object):

    def run(self, path = "downloads"):
        config = self.load_config()

        base_url = config.get("base_url", "https://ripe-core-sbx.platforme.com/api/")
        token = config.get("token", "")
        date_dir = config.get("date_dir", True)
        meta = config.get("meta", {})

        if date_dir:
            now = datetime.datetime.now()
            date_string = now.strftime("%Y-%m-%d_%H-%M-%S")
            path = os.path.join(path, date_string)

        if not os.path.exists(path):
            os.makedirs(path)

        with appier_console.ctx_loader(template = "{{spinner}} Loading") as thread:
            thread.template = "{{spinner}} Logging in to RIPE instance"
            ripe_api = ripe.API(base_url = base_url)
            ripe_api.login_pid(token)

            thread.template = "{{spinner}} Running a small sleep"
            time.sleep(0)

            thread.template = "{{spinner}} Starting order creation..."

            dimensions = config.get("dimensions", {})
            dimensions_order = dimensions.get("order", [])
            dimensions_l = []
            for name in dimensions_order:
                dimension = dimensions[name]
                dimensions_l.append(dimension)

            dimensions_p = list(itertools.product(*dimensions_l))
            dimensions_p.insert(0, None)

            models = config["models"]

            for index, model in enumerate(models):
                numbers = []
                pdf_paths = []

                thread.template = "{{spinner}} [%d/%d] Creating '%s' orders..." % (index + 1, len(models), model)

                for dimension in dimensions_p:
                    # tries to obtain the name of the color for the
                    # base part that is going to be use in the import
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

                    if dimension:
                        dimension_suffix = "-".join(dimension)
                        engraving_l = []
                        for index, dimension_part in enumerate(dimension):
                            engraving_l.append("%s:%s" % (dimension_part, dimensions_order[index]))
                        engraving_s = ".".join(engraving_l)
                    else:
                        dimension_suffix = None
                        engraving_s = None

                    # creates the contents dictionary that is going to be used
                    # as the basis for the import order operation
                    contents = dict(
                        brand = config["brand"],
                        model = model,
                        parts = parts,
                        size = config.get("size", 17)
                    )

                    # in case a valid engraving value is found (proper dimension
                    # is being read), then sets both the initials and the engraving
                    # values in the contents to generate proper order with initials
                    if engraving_s:
                        contents["initials"] = meta.get("initials", "Hello World")
                        contents["engraving"] = engraving_s

                    # creates the order according to the provided brand
                    # and model parts structure
                    order = ripe_api.import_order(
                        ff_order_id = str(uuid.uuid4()),
                        contents = json.dumps(contents)
                    )

                    report_base_url = meta.get("report_base_url", None)
                    if report_base_url:
                        secret_key = meta["secret_key"]
                        environment = meta.get("environment", "ripe-core-sbx")
                        report_url = "%s/api/orders/%d/report?environment=%s&key=%s" %\
                            (report_base_url, order["number"], environment, secret_key)
                        ripe_api.update_report_url_order(
                            order["number"],
                            report_url
                        )

                    # obtains the PDF contents for the report of the current
                    # order in iteration to latter save them
                    order_report = ripe_api.report_pdf(order["number"], order["key"])

                    if dimension_suffix:
                        model_name = "%s-%s.pdf" % (model, dimension_suffix)
                    else:
                        model_name = "%s.pdf" % model

                    # saves the model PDF with proper naming, respecting the
                    # naming standard of the engraving
                    model_path = os.path.join(path, model_name)
                    model_path = os.path.abspath(model_path)
                    model_file = open(model_path, "wb")
                    try: model_file.write(order_report)
                    finally: model_file.close()

                    pdf_paths.append(model_path)
                    numbers.append(order["number"])

                if config.get("remove", True):
                    for number in numbers: ripe_api.delete_order(number)

                if config.get("join", True):
                    model_name = "%s.all.pdf" % model
                    model_path = os.path.join(path, model_name)
                    model_path = os.path.abspath(model_path)
                    self.join_pdfs(model_path, pdf_paths)

        print("Finished generating report for %d orders\n" % len(models))
        print(MESSAGE)

    def join_pdfs(self, target_path, source_paths, remove = True):
        import PyPDF2

        target_file = open(target_path, "wb")

        pdf_files = []
        try:
            for source_path in source_paths:
                pdf_file = open(source_path, "rb")
                pdf_files.append(pdf_file)

            writer = PyPDF2.PdfFileWriter()
            for reader in map(PyPDF2.PdfFileReader, pdf_files):
                for index in range(reader.getNumPages()):
                    writer.addPage(reader.getPage(index))

            writer.write(target_file)
        finally:
            for pdf_file in pdf_files: pdf_file.close()
            target_file.close()

        if remove:
            for source_path in source_paths: os.remove(source_path)

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
