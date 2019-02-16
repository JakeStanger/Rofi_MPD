from setuptools import setup

setup(
    name='Rofi-MPD',
    version='1.0.0',
    install_requires=['python-mpd2'],
    py_modules=['rofi'],
    url='https://github.com/JakeStanger/Rofi_MPD',
    license='MIT',
    author='Jake Stanger',
    author_email='jakestanger@gmail.com',
    description='A rofi menu for interacting with MPD.',
    scripts=['rofi-mpd']
)
