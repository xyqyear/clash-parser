# Clash Parser HTTP API

This is an implementation of the Parser feature from CFW, but with HTTP API.

## Features

- **URL Parsing**: Parse YAML files from a given URL, which can be either a full URL or a shortened URL.
- **Parser Management**: The service is capable of handling multiple parsers for different URLs. Parsers can be added, updated, or removed via API endpoints.
- **Docker Support**: Project can be easily deployed using Docker.

The shortened URL mapping should be defined in the `url-mapping` entry in the `config.yaml` file.

The configuration is reloaded everytime a request is made to the server.

## Installation

### Using Docker

Make sure you have Docker and the compose plugin installed on your machine.

First, you should build the container with

```bash
docker compose build
```

Then, you can start the service using

```bash
docker compose up -d
```

### Using Poetry

You must have Python 3.11+ and Poetry installed on your machine.

Install dependencies using Poetry:

```bash
poetry install
```

Run the server using:

```bash
python -m clash_parser
```

## Usage

The service exposes several HTTP endpoints:

- `GET /parse?url={url}`: Returns the parsed YAML of the file at the provided URL.
- `GET /s/{short_url}`: Parses the YAML file at the URL corresponding to the provided short URL.
- `PUT /update?url={url}`: Updates the parser for the provided URL. The body of the request should contain the new parser.
- `POST /add`: Adds a new parser. The request should contain a `url` or `reg` parameter and the body should contain the new parser.
- `DELETE /remove?url={url}`: Removes the parser for the provided URL.

## TODO

- [x] add Dockerfile and docker-compose.yaml

## What's clash, cfw or parser?

I don't know.
