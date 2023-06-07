import random
import re

from ruamel.yaml import YAML


def process_command(yaml_dict, command):
    # this regex only matches `+` or `-` if it is preceded by a digit
    # so that we can use `+` or `-` in the locator
    locator, operation, value = re.match(
        r"^(.*?)((?<=\d)[+-]|=)(.*)$", command
    ).groups()

    parts = locator.split(".")
    keys = []
    temp_part = []
    for part in parts:
        if part.startswith("(") and not part.endswith(")"):
            temp_part.append(part[1:])
            continue
        elif part.endswith(")"):
            temp_part.append(part[:-1])
            keys.append(".".join(temp_part))
            temp_part = []
        else:
            if temp_part:
                temp_part.append(part)
            else:
                keys.append(part)

    if value.startswith("[]"):
        if "|" in value:
            value, regex = value.split("|", 1)
            pattern = re.compile(regex)
        else:
            pattern = re.compile(".*")

        if value == "[]proxyNames":
            value = [
                proxy["name"]
                for proxy in yaml_dict["proxies"]
                if re.search(pattern, proxy["name"])
            ]
        elif value == "[]groupNames":
            value = [
                group["name"]
                for group in yaml_dict["proxy-groups"]
                if re.search(pattern, group["name"])
            ]
        elif value == "[]shuffledProxyNames":
            value = [
                proxy["name"]
                for proxy in yaml_dict["proxies"]
                if re.search(pattern, proxy["name"])
            ]
            random.shuffle(value)

    target = yaml_dict
    for i in range(len(keys)):
        if keys[i].isdigit() or (keys[i].startswith("-") and keys[i][1:].isdigit()):
            if not isinstance(target, list):
                raise TypeError(
                    f'Invalid key {keys[i]} at {".".join(keys[:i])}: it is not an array'
                )
            key = int(keys[i])
            if i < len(keys) - 1:
                target = target[key]
        elif isinstance(target, list):
            key = next(
                (
                    j
                    for j, v in enumerate(target)
                    if "name" in v and v["name"] == keys[i]
                ),
                -1,
            )
            if key == -1:
                raise KeyError(
                    f"Invalid key {keys[i]} at {'.'.join(keys[:i])}: can't find object with name {keys[i]}"
                )
            if i < len(keys) - 1:
                target = target[key]
        elif isinstance(target, dict):
            key = keys[i]
            if i < len(keys) - 1:
                target = target[key]
        else:
            raise TypeError(
                f'Invalid key {keys[i]} at {".".join(keys[:i])}: it is not an array or object'
            )

    if operation == "=":
        target[key] = value
    elif operation == "+":
        if not isinstance(target, list):
            raise TypeError(f'Operation "+" is only supported for array at {locator}')
        target.insert(key, value)
    elif operation == "-":
        if not isinstance(target, list):
            raise TypeError(f'Operation "-" is only supported for array at {locator}')
        target.pop(key)


def process_yaml(original_yaml: str, processing_rules: dict, stream) -> str:
    yaml = YAML()
    yaml.preserve_quotes = True
    original_dict = yaml.load(original_yaml)

    for key, value in processing_rules.items():
        if "append-" in key:
            key = key.replace("append-", "")
            original_dict[key].extend(value)
        elif "prepend-" in key:
            key = key.replace("prepend-", "")
            original_dict[key] = value + original_dict[key]
        elif "mix-" in key:
            key = key.replace("mix-", "")
            original_dict[key].update(value)
        elif "commands" in key:
            for command in value:
                process_command(original_dict, command)
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.dump(original_dict, stream)
