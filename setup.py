from setuptools import setup, find_packages
import os

version = '1.44.dev0'

README = open("README.rst").read()
HISTORY = open(os.path.join("docs", "HISTORY.rst")).read()

setup(name='ulearn.theme',
      version=version,
      description="",
      long_description=README + "\n" + HISTORY,
      classifiers=[
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='plone genweb theme ulearn communities comunitats',
      author='UPCnet Plone Team',
      author_email='plone.team@upcnet.es',
      url='https://github.com/upcnet/ulearn.theme.git',
      license='gpl',
      packages=find_packages(exclude=['ez_setup']),
      # package_dir={'': 'src'},
      namespace_packages=['ulearn', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'genweb.theme'
      ],
      extras_require={'test': ['plone.app.testing[robot]>=4.2.2']},
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
