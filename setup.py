from setuptools import setup, find_packages

long_desc = '''
This package contains Cloudformation support for Sphinx.

This package enables you to use the 'cfn' domain to create
cloudformation resources. It also contains a parser for CloudFormation
resources to output RST.

See https://github.com/ofosos/cfn-doctemplate for example usage.
'''

requires = ['Sphinx>=0.6',
            'sphinxcontrib-domaintools>=0.1',
            'pyyaml',
            'requests']

setup(
    name='sphinxcontrib-cloudformation',
    version='0.1',
    url='http://github.com/ofosos/sphinx-cfn',
    download_url='http://pypi.python.org/pypi/cfnsphinx',
    license='GPLv3',
    author='Mark Meyer',
    author_email='mark@ofosos.org',
    description='Cloudformation domain for Sphinx',
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
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
    entry_points={
        'console_scripts': ['cfnsphinx-build=cfnsphinx.cfn_build:main'],
    },

)
