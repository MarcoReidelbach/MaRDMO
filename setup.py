import re

from setuptools import find_packages, setup

# get metadata from mudule using a regexp
with open('MaRDMO/__init__.py') as f:
    metadata = dict(re.findall(r'__(.*)__ = [\']([^\']*)[\']', f.read()))

setup(
    name=metadata['title'],
    version=metadata['version'],
    author=metadata['author'],
    author_email=metadata['email'],
    maintainer=metadata['author'],
    maintainer_email=metadata['email'],
    license=metadata['license'],
    url='https://github.com/MarcoReidelbach/MaRDMO',
    description=u'Plugin to document and query interdisciplinary workflows using the MaRDI Portal.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.10'
    ],
    packages=find_packages(),
    package_data = {'MaRDMO':['templates/MaRDMO/*.html','templates/MaRDMO/*.md','templates/MaRDMO/*.mediawiki','data/*.json']},
    include_package_data=True,

    install_requires=['bibtexparser','langdetect','pylatexenc','wikibaseintegrator']
)

