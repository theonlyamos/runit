from importlib.metadata import entry_points
from setuptools import setup, find_packages

VERSION = '0.4.5'

with open('README.md', 'rt') as file:
    LONG_DESCRIPTION = file.read()

setup(
    name='runit-cli',
    version=VERSION,
    author='Amos Amissah',
    author_email='theonlyamos@gmail.com',
    description='Develop serverless applications',
    long_description=LONG_DESCRIPTION,
    long_description_content_type = "text/markdown",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests>=2.28.0',
        'python-dotenv>=1.0.0',
        'fastapi>=0.100.0',
        'passlib>=1.7.4',
        'docker>=6.0.0',
        'uvicorn>=0.23.0',
        'websockets>=11.0',
        'keyring>=24.0.0',
    ],
    extras_require={
        'ai': ['openai>=1.0.0'],
        'dev': ['pytest>=7.0.0', 'pytest-cov>=4.0.0'],
    },
    keywords='python3 runit developer serverless architecture docker',
    project_urls={
        'Source': 'https://github.com/theonlyamos/runit',
        'Tracker': 'https://github.com/theonlyamos/runit/issues',
    },
    python_requires='>=3.10',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
    entry_points={
        'console_scripts': [
            'runit=runit.cli:main',
        ],
    }
)
