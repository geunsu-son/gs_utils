from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='gs_utils',
    version='0.2.0',
    description='geunsu-son\'s Personal Python Utility Library',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='geunsu-son',
    author_email='gnsu0705@gmail.com',
    url='https://github.com/your-username/gs_utils',
    packages=find_packages(),
    install_requires=[
        'google-api-python-client>=2.0.0',
        'google-auth>=2.0.0',
        'google-auth-oauthlib>=1.0.0',
        'google-auth-httplib2>=0.1.0',
        'pandas>=1.3.0',
        'pyautogui>=0.9.50',
        'pywinauto>=0.6.8',
    ],
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'Topic :: Desktop Environment',
        'Topic :: System :: Hardware',
    ],
    keywords='google api utility functions decorators automation windows gui',
    project_urls={
        'Bug Reports': 'https://github.com/your-username/gs_utils/issues',
        'Source': 'https://github.com/your-username/gs_utils',
    },
)
