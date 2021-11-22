from setuptools import setup

with open('README.rst') as fd:
    long_description = fd.read()

setup(
    name='bs4tag',
    version='0.1.0',
    package_data={"bs4tag": ["py.typed"]},
    packages=['bs4tag'],
    python_requires='>=3.2.0',
    install_requires=['typing;python_version<"3.5"', 'bs4'],
    author='ceprio',
    author_email='c.pypi@zone-c4.com',
    url='https://www.yattag.org',
    keywords=["html", "template", "templating", "xml", "document", "form", "rendering", "beautifulsoup"],
    description="""\
Generate HTML or XML in a pythonic way. Pure python alternative to web template engines. \
Based on BeautifulSoup parser. \
Can fill HTML forms with default values and error messages.""",
    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
