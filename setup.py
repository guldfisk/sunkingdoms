from setuptools import setup
import os


def package_files(directory):
    paths = []
    for path, directories, file_names in os.walk(directory):
        for filename in file_names:
            paths.append(os.path.join('..', path, filename))
    return paths


extra_files = package_files('sunkingdoms')


setup(
    name='sunkingdoms',
    version='1.0',
    packages=['sunkingdoms'],
    package_data={'': extra_files},
    dependency_links = [
        'https://github.com/guldfisk/yeetlong/tarball/master#egg=yeetlong-1.0',
        'https://github.com/guldfisk/eventdispatch/tarball/master#egg=eventdispatch-1.0',
        'https://github.com/guldfisk/eventtree/tarball/master#egg=eventtree-1.0',
        'https://github.com/guldfisk/gameframe/tarball/master#egg=gameframe-1.0',
    ],
    install_requires = [
        'yeetlong',
        'eventdispatch',
        'eventtree',
        'gameframe',
    ],

)