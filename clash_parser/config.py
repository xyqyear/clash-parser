import re
from io import StringIO

import aiofiles
import ruamel.yaml

yaml = ruamel.yaml.YAML(typ="rt")
yaml.preserve_quotes = True
yaml.indent(mapping=2, sequence=4, offset=2)


class Config:
    def __init__(self, path):
        self.path = path
        self.yaml = None

    async def load(self):
        async with aiofiles.open(self.path, "r") as f:
            self.yaml = yaml.load(await f.read())

    def load_sync(self):
        with open(self.path, "r") as f:
            self.yaml = yaml.load(f.read())

    async def save(self):
        buffer = StringIO()
        yaml.dump(self.yaml, buffer)
        async with aiofiles.open(self.path, "w") as f:
            await f.write(buffer.getvalue())

    def save_sync(self):
        with open(self.path, "w") as f:
            yaml.dump(self.yaml, f)

    def get_full_url(self, short_url):
        url_mapping = self.yaml["url-mapping"]
        if short_url not in url_mapping:
            return None
        return url_mapping[short_url]

    # since we are not dealing with a lot of parsers, we can just iterate through them
    def find_index(self, url):
        for i, p in enumerate(self.yaml["parsers"]):
            if "url" in p and p["url"] == url:
                return i
            if "reg" in p and re.match(p["reg"], url):
                return i
        return -1

    def get_parser_for_url(self, url):
        index = self.find_index(url)
        if index == -1:
            return None
        return self.yaml["parsers"][index]["yaml"]

    def update_parser_for_url(self, url, new_parser):
        index = self.find_index(url)
        if index == -1:
            return
        self.yaml["parsers"][index]["yaml"] = new_parser

    # assume only one parser for each url
    def remove_parser_for_url(self, url):
        index = self.find_index(url)
        if index == -1:
            return
        del self.yaml["parsers"][index]

    def add_parser(self, url, parser):
        self.yaml["parsers"].append({"url": url, "yaml": parser})

    def add_parser_regex(self, regex, parser):
        self.yaml["parsers"].append({"reg": regex, "yaml": parser})
