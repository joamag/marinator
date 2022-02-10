#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import json
import time
import uuid
import datetime
import itertools

import appier
import appier_console

import ripe

VERSION = "0.2.2"
""" The version number of the Marinator utility
to be used when printing diagnostics """

LABEL = "marinator/%s" % VERSION
""" The final composed version of the utility label """

LABEL_FULL = "%s - The power of Marina to everyone 🤖" % LABEL
""" The complete version of the label including a simple
sub-title element """

MESSAGE = """To Marina, the QA team and all the other members that invest a significant amount of their time in tasks that are necessary and that require extreme resilience, my deppest appreciation, you represent the heart and soul of PlatformE.
Marina two words for you - You rock 🤘
This tool has been made with ❤️"""
""" The message that is going to be printed at the
end of the utility execution """

class Marinator(object):

    def run(self, path = "downloads"):
        print(LABEL_FULL)

        config = self.load_config()

        brand = config["brand"]
        models = config["models"]
        base_url = config.get("base_url", "https://ripe-core-sbx.platforme.com/api/")
        token = config.get("token", "")
        date_dir = config.get("date_dir", True)
        handlers = config.get("handlers", [])
        meta = config.get("meta", {})

        # extracts some of the configuration options
        # that can be used to control the util behaviour
        delete = config.get("delete", True)
        join = config.get("join", True)

        # adds the name of the brand as a valid handler, taking
        # into consideration that if the handler does not exist
        # a gracefull handling of the error will occur
        handlers.append(brand)
        handlers = set(handlers)

        if date_dir:
            now = datetime.datetime.now()
            date_string = now.strftime("%Y-%m-%d_%H-%M-%S")
            path = os.path.join(path, date_string)

        path = os.path.abspath(path)
        if not os.path.exists(path): os.makedirs(path)

        with appier_console.ctx_loader(template = "{{spinner}} Loading") as thread:
            thread.set_template("{{spinner}} Logging in to RIPE instance")
            ripe_api = ripe.API(base_url = base_url)
            ripe_api.login_pid(token)

            thread.set_template("{{spinner}} Running a small sleep")
            time.sleep(0)

            thread.set_template("{{spinner}} Starting order creation...")

            dimensions = config.get("dimensions", {})
            dimensions_order = dimensions.get("order", [])
            dimensions_l = []
            for name in dimensions_order:
                dimension = dimensions[name]
                dimensions_l.append(dimension)

            # builds the complete set of dimensions permutations from the
            # list of dimensions and then adds the "special" empty case
            # to the beggining of the sequence
            dimensions_p = list(itertools.product(*dimensions_l))
            dimensions_p.insert(0, None)

            for index, model in enumerate(models):
                numbers = []
                pdf_paths = []

                thread.set_template("{{spinner}} [%d/%d] Creating '%s' orders..." % (index + 1, len(models), model))

                for dimension_p in dimensions_p:
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

                    # in case a valid dimension is defined then we need
                    # to try to generate the engraving value for the
                    # dimension, properly validating the same string
                    if dimension_p:
                        # obtains the map of properties that can be used
                        # to validate if the current dimension specification
                        # is compatible with the current model
                        config_brand = ripe_api.config_brand(brand, model)
                        initials = config_brand.get("initials", {})
                        properties = initials.get("properties", [])
                        properties_m = self._build_properties_m(properties)

                        # in case the properties are considered to be not valid
                        # meaning that at least of the dimension value is not
                        # present in the model's initials properties definition
                        # then we must skip the current iteration to avoid the
                        # generation of an invalid engraving value for the order
                        if not self._validate_dimension(dimension_p, dimensions_order, properties_m):
                            continue

                        # iterates over the complete set of dimension permutation
                        # elements to build the engraving string list
                        engraving_l = []
                        for index, dimension_value in enumerate(dimension_p):
                            # using the current index in iteration to obtain the name of the
                            # dimension currently in iteration, and be able to construct
                            # the engraving part corresponding to the current dimension
                            dimension_name = dimensions_order[index]

                            # creates the new engraving partial element and adds it to
                            # the list that is going to be used in the engraving label generation
                            engraving_l.append("%s:%s" % (dimension_value, dimension_name))

                        engraving_s = ".".join(engraving_l)
                        dimension_suffix = "-".join(dimension_p)
                    else:
                        engraving_s = None
                        dimension_suffix = "plain"

                    # creates the contents dictionary that is going to be used
                    # as the basis for the import order operation
                    contents = dict(
                        brand = brand,
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

                    try:
                        # creates the order according to the provided brand
                        # and model parts structure
                        order = ripe_api.import_order(
                            ff_order_id = str(uuid.uuid4()),
                            contents = json.dumps(contents),
                            meta = ["generator:%s" % LABEL, "mood:Built with ❤️"]
                        )
                    except appier.HTTPError as exception:
                        print("Exception - %s" % str(exception))
                        continue

                    # iterates over the complete set of handlers expected to
                    # be executed for the current order and runs them
                    for handler in handlers:
                        handler_name = "_handle_%s" % handler
                        if not hasattr(self, handler_name): continue
                        handler_method = getattr(self, handler_name)
                        handler_method(ripe_api, config = config, order = order)

                    # obtains the PDF contents for the report of the current
                    # order in iteration to latter save them
                    order_report = ripe_api.report_pdf(order["number"], order["key"])

                    # saves the model PDF with proper naming, respecting the
                    # naming standard of the engraving
                    model_name = "%s-%s.pdf" % (model, dimension_suffix)
                    model_path = os.path.join(path, model_name)
                    model_path = os.path.abspath(model_path)
                    model_file = open(model_path, "wb")
                    try: model_file.write(order_report)
                    finally: model_file.close()

                    pdf_paths.append(model_path)
                    numbers.append(order["number"])

                if delete:
                    for number in numbers: ripe_api.delete_order(number)

                if join:
                    model_name = "%s.pdf" % model
                    model_path = os.path.join(path, model_name)
                    model_path = os.path.abspath(model_path)
                    self.join_pdfs(model_path, pdf_paths)

        print("Finished generating reports for %d orders in %s\n" % (len(models), path))
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

    def _validate_dimension(self, dimension_p, dimensions_order, properties_m):
        """
        Makes sure that the current dimension in iteration is valid
        for the model in question.

        This verification is done by validating the dimension against
        the properties section of the model's config.

        :type dimension_p: List
        :param dimension_p: The dimension permutation that is going to be used
        fore the validation process.
        :type dimensions_order: List
        :param dimensions_order: The sequence that defines the order from which
        the dimension should be defined.
        :type properties_m: Dictionary
        :param properties_m: The map that contains the complete set of
        properties for the model, the provided dimension permutation is
        going to be validated "against" it.
        :rtype: bool
        :return: If the provided dimension permutation is valid according
        to the provided properties map.
        """

        for index, dimension_value in enumerate(dimension_p):
            # using the current index in iteration to obtain the name of the
            # dimension currently in iteration, and be able to construct
            # the engraving part corresponding to the current dimension
            dimension_name = dimensions_order[index]

            # in case the current dimension value is not defined in the
            # properties definition, then we must skip the current
            # order import as it's considered invalid
            if not dimension_value in properties_m.get(dimension_name, []):
                return False

        return True

    def _build_properties_m(self, properties):
        properties_m = dict()
        for property in properties:
            sequence = properties_m.get(property["type"], [])
            sequence.append(property["name"])
            properties_m[property["type"]] = sequence
        return properties_m

    def _handle_hermes(self, ripe_api, config = {}, order = {}):
        meta = config.get("meta", {})
        report_base_url = meta.get("report_base_url", None)
        secret_key = meta.get("secret_key", None)
        environment = meta.get("environment", "ripe-core-sbx")
        if report_base_url and secret_key:
            report_url = "%s/api/orders/%d/report?environment=%s&key=%s" %\
                (report_base_url, order["number"], environment, secret_key)
            ripe_api.update_report_url_order(
                order["number"],
                report_url
            )

if __name__ == "__main__":
    marinator = Marinator()
    marinator.run()
else:
    __path__ = []
