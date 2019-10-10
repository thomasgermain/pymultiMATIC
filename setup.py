from setuptools import setup, find_packages

from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='pymultiMATIC',
      version='0.0.1',
      description='Python interface with Vaillant multiMATIC',
      long_description_content_type='text/markdown',
      long_description=long_description,
      url='https://github.com/thomasgermain/pymultiMATIC.git',
      author='Thomas Germain',
      author_email='12560542+thomasgermain@users.noreply.github.com',
      license='MIT',
      packages=find_packages(exclude=
                             ('tests', 'tests/*', '/tests', '/tests/*')),
      zip_safe=False,
      setup_requires=["pytest-runner"],
      install_requires=[
          "requests>=2.20.0,<3.0.0",
          "jsonpickle>=1.0,<2.0"
      ],
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Development Status :: 4 - Beta',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Topic :: Home Automation'
      ]
      )
