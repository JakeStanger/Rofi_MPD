from setuptools import setup

setup(
    name='Rofi-MPD',
    version='2.2.1',
    install_requires=['python-mpd2', 'mutagen', 'toml', 'appdirs'],
    packages=['rofi', 'rofi_mpd'],
    url='https://github.com/JakeStanger/Rofi_MPD',
    license='MIT',
    author='Jake Stanger',
    author_email='mail@jstanger.dev',
    description='A Rofi menu for interacting with MPD.',
    scripts=['bin/rofi-mpd']
)
