from setuptools import setup, find_packages

setup(
    name="pyseq_library",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "mido",
        "python-rtmidi",
        "windows-curses"
    ],
)