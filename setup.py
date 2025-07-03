from setuptools import setup, find_packages

setup(
    name='gs_utils',
    version='0.1.0',
    description='A collection of utility functions by geunsu-son',
    author='geunsu-son',
    author_email='gnsu0705@gmail.com',
    packages=find_packages(),
    install_requires=[
        'google-api-python-client',
        'google-auth',
        'google-auth-oauthlib',
    ],
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
