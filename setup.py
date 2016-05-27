from setuptools import setup

exec(compile(open('hermes/_version.py').read(), 'hermes/_version.py', 'exec'))

setup(name='hermes',
      version = __version__,
      description = 'file tranfer monitor protocols ftp, sftp',
      url = 'https://github.com/cfauchard/hermes',
      author = 'Christophe Fauchard',
      author_email = 'christophe.fauchard@gmail.com',
      license = 'GPLV3',
      packages = ['hermes'],
      scripts = ['bin/hermescmd.py'],
      install_requires=[
            'zeus',
            'paramiko'
      ],
      zip_safe = False)
