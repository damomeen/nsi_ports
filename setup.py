from setuptools import setup, find_packages

setup(name='nsi_ports',
      version='0.1',
      author='Damian Parniewicz',
      author_email='damian.parniewicz@gmail.com',
      package_dir = {'nsi_ports': 'src'},
      packages=find_packages(),
      description = ("Python daemon which exposes Geant BoD/NSI ports "
                                   "over HTTP/REST api."),
      keywords = 'Geant BoD NSI REST',
      install_requires=['flask'],
      include_package_data = True,
      package_data={
        'nsi_ports': ['nsi-ports.conf.example']
      },
)
