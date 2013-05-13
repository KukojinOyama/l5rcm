# -*- mode: python -*-

def Datafiles(*filenames, **kw):
    import os
    
    def datafile(path, strip_path=True):
        parts = path.split('/')
        path = name = os.path.join(*parts)
        if strip_path:
            name = os.path.basename(path)
        return name, path, 'DATA'

    strip_path = kw.get('strip_path', False)
    return TOC(
        datafile(filename, strip_path=strip_path)
        for filename in filenames
        if os.path.isfile(filename))

namefiles = Datafiles('share/l5rcm/male.txt', 'share/l5rcm/female.txt')
logofiles = Datafiles('share/l5rcm/banner_s.png')
dbfile    = Datafiles('share/l5rcm/l5rdb.sqlite')

a = Analysis([os.path.join(HOMEPATH,'support/_mountzlib.py'), os.path.join(HOMEPATH,'support/useUnicode.py'), 'l5rcm.py'],
             pathex=['./l5rcm'])
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
          name=os.path.join('build/pyi.linux2/l5rcm', 'l5rcm'),
          debug=False,
          strip=False,
          upx=True,
          console=1 )
coll = COLLECT( exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               namefiles,
               logofiles,
               dbfile,
               strip=False,
               upx=True,
               name=os.path.join('dist', 'l5rcm'))
