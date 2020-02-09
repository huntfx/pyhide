import os
from setuptools import setup, find_packages


# Get the README.md text
with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r') as f:
    readme = f.read()

# Parse pyhide.py for a version
with open(os.path.join(os.path.dirname(__file__), 'pyhide.py'), 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = eval(line.split('=')[1].strip())
            break
    else:
        raise RuntimeError('no version found')

# Get the pip requirements
with open(os.path.join(os.path.dirname(__file__), 'requirements.txt'), 'r') as f:
    requirements = [line.strip() for line in f]

setup(
    name = 'pyhide',
    packages = find_packages(),
    version = version,
    license='MIT',
    description = 'Use steganography to hide data in images.',
    long_description=readme,
    long_description_content_type='text/markdown',
    author = 'Peter Hunt',
    author_email='peterh@blue-zoo.co.uk',
    py_modules=['pyhide'],
    url = 'https://github.com/Peter92/pyhide',
    download_url = 'https://github.com/Peter92/pyhide/archive/{}.tar.gz'.format(version),
    project_urls={
        #'Documentation': 'https://github.com/Peter92/pyhide/wiki',
        'Source': 'https://github.com/Peter92/pyhide',
        'Issues': 'https://github.com/Peter92/pyhide/issues',
    },
    keywords = ['steganography', 'hide', 'encode', 'image', 'imaging', 'lsb'],
    install_requires=requirements,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Multimedia :: Graphics'
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    python_requires=('>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*')
)
