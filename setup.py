from setuptools import setup

setup(
    name='Rofi-MPD',
    version='1.1.0',
    install_requires=['python-mpd2', 'mutagen'],
    packages=['rofi', 'rofi_mpd'],
    # py_modules=['rofi', 'rofi-mpd'],
    url='https://github.com/JakeStanger/Rofi_MPD',
    license='MIT',
    author='Jake Stanger',
    author_email='mail@jstanger.dev',
    description='A Rofi menu for interacting with MPD.',
    scripts=['bin/rofi-mpd']
)
