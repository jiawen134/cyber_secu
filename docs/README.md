# Windows RAT Classroom Demo Project

## Project Overview

This project demonstrates a minimal Remote Administration Tool (RAT) for educational purposes, teaching socket communication, multi-threading, and cybersecurity concepts in isolated environments.

### Architecture
```
Operator CLI <--> C2 Server <--> Client Agent(s)
```

## Features
- Screenshot capture
- Popup message display  
- Heartbeat monitoring
- Multi-client support
- PyInstaller packaging

## Quick Start

1. **Setup Environment**
   ```cmd
   setup.bat
   ```

2. **Start C2 Server**
   ```cmd
   python server/server.py
   ```

3. **Start Operator CLI**
   ```cmd
   python operator/operator.py
   ```

4. **Start Client**
   ```cmd
   python client/client.py
   ```

5. **Build Executable**
   ```cmd
   cd build && build_client.bat
   ```

## Educational Use Only

⚠️ **WARNING**: This is for educational purposes only. Use only in isolated environments with proper authorization.

## Project Structure
```
cyber_secu/
├── server/          # C2 Server
├── client/          # RAT Client
├── operator/        # CLI Interface
├── build/           # Build scripts
└── docs/           # Documentation
``` 