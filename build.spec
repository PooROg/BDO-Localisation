# build.spec

# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['main.py'],
             pathex=[],
             binaries=[],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             datas=[('font/RU/pearl.ttf', 'font/RU'),
                    ('font/EN/pearl.ttf', 'font/EN'),
                    ('font/JP/pearl.ttf', 'font/JP'),
                    ('font/TW/pearl.ttf', 'font/TW'),
                    ('assets/icon.ico', 'assets')
                    ],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas, [],
          name='BDO Localisation',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          )