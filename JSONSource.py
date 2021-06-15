import os
import json

from parmenides.conf import settings
from parmenides.document import Document, Section
from parmenides.source import DocumentSource


class JSONSource(DocumentSource):
    @classmethod
    def get_estimate(cls, arguments):
        filename = arguments[0]
        if len(arguments) > 1:
            json_starters = arguments[1:]
        with open(filename, "r", encoding="utf-8") as fp:
            cls.json_obj = json.load(fp)
            cls.estimate = len(cls.json_obj)
        for code in json_starters:
            cls.json_obj = cls.json_obj[code]

    @classmethod
    def get_documents(cls, filenames):
        for document in cls.json_obj:
            sections = [Section(name="Main", content=document["description"][0])]
            title = document["title"]

            yield Document(
                identifier=title,
                title=os.path.basename(filenames[0]),
                sections=sections,
                collections=[settings.COLLECTION_NAME],
            )
