# Getting Started with SPIRT

## Requirements

- Python 3.11 or newer.
- Network access to the public pages you are authorized to research.

## Install

```bash
python -m pip install spirt
```

For the optional API:

```bash
python -m pip install 'spirt[api]'
```

For development:

```bash
python -m pip install -e '.[dev]'
```

## Discover providers

```bash
spirt providers
```

This shows the provider registry and the public collection capabilities declared by each provider.

## Collect a public profile

```bash
spirt profile https://github.com/example --json
```

Human-readable output is available without `--json`. Add `--evidence` to inspect field-level provenance.

## Discover profile URLs

SPIRT can extract supported profile URLs from text or HTML without requesting the discovered URLs:

```bash
spirt discover input.txt
```

## Generate a research report

```bash
spirt report https://github.com/example https://www.linkedin.com/in/example --markdown
```

Use `--output report.md` to save the report.

## API

Start the optional service locally:

```bash
uvicorn spirt.api:create_app --factory --host 127.0.0.1 --port 8000
```

Then inspect `/health`, `/v1/providers`, `/v1/profile`, and `/v1/report`.

## Recommended workflow

1. Start with a profile URL or a username.
2. Resolve candidate profile URLs deterministically.
3. Collect only legitimately public information.
4. Inspect evidence provenance before drawing conclusions.
5. Treat cross-platform matches as signals, not proof of identity.
6. Export a report when the research needs to be reviewed or shared.
