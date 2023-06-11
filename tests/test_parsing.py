import pytest

from clash_parser.parsing import process_command

command_test_pairs = [
    (
        (
            {
                "proxies": [
                    {"name": "proxy1", "type": "http"},
                    {"name": "proxy2", "type": "http"},
                ]
            },
            "proxies.0.name=proxy3",
        ),
        {
            "proxies": [
                {"name": "proxy3", "type": "http"},
                {"name": "proxy2", "type": "http"},
            ]
        },
    ),
    (
        (
            {
                "proxies": [
                    {"name": "proxy1", "type": "http"},
                    {"name": "proxy2", "type": "http"},
                ]
            },
            "proxies.proxy1.type=socks5",
        ),
        {
            "proxies": [
                {"name": "proxy1", "type": "socks5"},
                {"name": "proxy2", "type": "http"},
            ]
        },
    ),
    (
        (
            {
                "proxies": [
                    {"name": "proxy1", "type": "http"},
                    {"name": "proxy2", "type": "http"},
                ]
            },
            "proxies.0-",
        ),
        {"proxies": [{"name": "proxy2", "type": "http"}]},
    ),
    (
        (
            {
                "proxy-groups": [
                    {
                        "name": "group1",
                        "type": "select",
                        "proxies": ["proxy1", "proxy2"],
                    },
                    {"name": "group2", "type": "select"},
                ]
            },
            "proxy-groups.0.proxies.0=proxy3",
        ),
        {
            "proxy-groups": [
                {
                    "name": "group1",
                    "type": "select",
                    "proxies": ["proxy3", "proxy2"],
                },
                {"name": "group2", "type": "select"},
            ]
        },
    ),
    (
        (
            {
                "proxy-groups": [
                    {
                        "name": "group1",
                        "type": "select",
                        "proxies": ["proxy1", "proxy2"],
                    },
                    {"name": "group2", "type": "select"},
                ]
            },
            "proxy-groups.0.proxies.0-",
        ),
        {
            "proxy-groups": [
                {"name": "group1", "type": "select", "proxies": ["proxy2"]},
                {"name": "group2", "type": "select"},
            ]
        },
    ),
    (
        (
            {
                "proxy-groups": [
                    {
                        "name": "group1",
                        "type": "select",
                        "proxies": ["proxy1", "proxy2"],
                    },
                    {"name": "group2", "type": "select"},
                ]
            },
            "proxy-groups.0.proxies.0+proxy0",
        ),
        {
            "proxy-groups": [
                {
                    "name": "group1",
                    "type": "select",
                    "proxies": ["proxy0", "proxy1", "proxy2"],
                },
                {"name": "group2", "type": "select"},
            ]
        },
    ),
    (
        (
            {
                "proxies": [
                    {"name": "proxy1", "type": "http"},
                    {"name": "proxy2", "type": "http"},
                ],
                "proxy-groups": [
                    {"name": "group1", "type": "select", "proxies": ["DIRECT"]},
                    {"name": "group2", "type": "select"},
                ],
            },
            "proxy-groups.0.proxies=[]proxyNames",
        ),
        {
            "proxies": [
                {"name": "proxy1", "type": "http"},
                {"name": "proxy2", "type": "http"},
            ],
            "proxy-groups": [
                {
                    "name": "group1",
                    "type": "select",
                    "proxies": ["proxy1", "proxy2"],
                },
                {"name": "group2", "type": "select"},
            ],
        },
    ),
    (
        (
            {
                "hosts": {
                    "google.com": "111.222.333.444",
                    "facebook.com": "111.222.333.444",
                }
            },
            "hosts.(google.com)-",
        ),
        {"hosts": {"facebook.com": "111.222.333.444"}},
    ),
    (
        (
            {
                "hosts": {
                    "google.com": "111.222.333.444",
                    "facebook.com": "111.222.333.444",
                }
            },
            "hosts-",
        ),
        {},
    ),
]


@pytest.mark.parametrize("yaml_command_pair, expected", command_test_pairs)
def test_process_command(yaml_command_pair, expected):
    yaml_dict, command = yaml_command_pair
    process_command(yaml_dict, command)
    assert yaml_dict == expected
