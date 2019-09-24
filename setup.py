from setuptools import setup

setup(
    name='Rofi-MPD',
    version='1.0.2',
    install_requires=['python-mpd2'],
    packages=['rofi', 'rofi-mpd'],
    # py_modules=['rofi', 'rofi-mpd'],
    url='https://github.com/JakeStanger/Rofi_MPD',
    license='MIT',
    author='Jake Stanger',
    author_email='jakestanger@gmail.com',
    description='A Rofi menu for interacting with MPD.',
    scripts=['bin/rofi-mpd']
)
