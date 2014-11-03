import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "Amazon",
    version = "0.0.0",
    scripts = ['bin/train_lda.py'],
    author = "Sharad Vikram",
    packages=['amazon'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
     entry_points = {
        'console_scripts': [
            'train_lda = train_lda:main']
    }
)
