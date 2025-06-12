# Windows RAT Classroom Demo Project

A minimal Remote Administration Tool (RAT) implementation for cybersecurity education and classroom demonstrations.

## Features

- **C2 Server**: Multi-client command and control server
- **Client Agent**: Reverse connection RAT client
- **Operator CLI**: Command line interface for operators
- **Screenshot**: Capture and retrieve screenshots
- **Popup**: Display message boxes on target systems
- **Packaging**: PyInstaller executable generation

## Quick Start

1. **Setup**: Run `setup.bat` to install dependencies
2. **Server**: `python server/server.py`
3. **Operator**: `python operator/operator.py`  
4. **Client**: `python client/client.py`
5. **Build**: `cd build && build_client.bat`

## Architecture

```
┌─────────────────┐    JSON/TCP    ┌─────────────────┐
│  Operator CLI   │ ◄─────────────► │   C2 Server     │
└─────────────────┘                └─────────┬───────┘
                                             │
                                             │ JSON/TCP
                                             ▼
                                   ┌─────────────────┐
                                   │ Client Agent(s) │
                                   └─────────────────┘
```

## Documentation

See `docs/README.md` for comprehensive documentation, demo walkthrough, and blue team analysis.

## Ethical Guidelines

- Only use on systems you own
- Isolated virtual machine environments only
- Proper authorization required
- Educational purposes only
- Follow local laws and regulations

---
