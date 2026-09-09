# SPIRT

## Social Profile Intelligence Research Toolkit

SPIRT is an open-source OSINT toolkit for researching and analyzing publicly available social-profile information.

The project uses a modular provider architecture so individual social platforms can be supported independently. The initial provider target is Facebook public-profile research, with additional platforms planned for future releases.

### Scope

SPIRT is intended for legitimate OSINT, security research, investigation, and research workflows using information that is publicly accessible. It does not attempt to bypass privacy controls, authentication, or access restrictions.

### Status

🚧 Early development. The CLI and project foundation are being established before provider implementations are added.

### Installation

```bash
python -m pip install spirt
```

### Usage

```bash
spirt --help
spirt version
spirt profile https://www.facebook.com/example
```

### Development

```bash
python -m pip install -e ".[dev]"
pytest
ruff check .
```

### License

MIT License. See `LICENSE`.
