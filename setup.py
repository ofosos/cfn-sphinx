import sys, os

from setuptools import setup, find_packages

long_desc = '''
This package contains Cloudformation support for Sphinx

'''

requires = ['Sphinx>=0.6', 'sphinxcontrib-domaintools>=0.1', 'pyyaml']

setup(
    name='sphinxcontrib-cloudformation',
    version='0.1',
    url='http://github.com/ofosos/sphinx-cfn',
    download_url='http://pypi.python.org/pypi/sphinxcontrib-cloudformation',
    license='BSD',
    author='Mark Meyer',
    author_email='mark@ofosos.org',
    description='Cloudformation extension for Sphinx',
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['cfnsphinx'],
    entry_points = {
        'console_scripts': ['cfnsphinx-build=cfnsphinx.cfn_build:main'],
    },

)
