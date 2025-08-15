from distutils.core import setup
import py2exe

setup(console=['starstdb_main.py'],
      data_files=[('starstdb.ini','starstdb.ini')],
      #version_info={'version':'0.1'}
      )
