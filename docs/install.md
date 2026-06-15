# Install

ASF-R v1.0-rc1 is packaged as a Python project with a console entry point.

```powershell
python -m pip install -e .
asf demo
```

The editable install exposes the `asf` command while keeping the repository local
and inspectable.

## Verify

```powershell
python -m unittest discover tests
python -m asf.cli doctor
python -m asf.cli demo
python -m asf.cli dogfood run
```

## Non-Claim Lock

Installability is not production authority. ASF-R v1.0-rc1 is a bounded release
candidate for reproducible local and remote verification. It does not claim
production security, formal verification, autonomous safety, or general repair
authority.
