import os
import sys
from setuptools import setup

if sys.version_info < (3, 4):    # Need to find minimum version that works
    print("Sorry, django-temperature-monitor currently requires Python 3.4+.")
    sys.exit(1)

# From: https://hynek.me/articles/sharing-your-labor-of-love-pypi-quick-and-dirty/
def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

install_requires = [
    "Django>=2,<3",    # Need to find minimum version that works
    "beautifulsoup4>=4.6.3",    # Need to find minimum version that works
    "django-project-home-templatetags>=0.1.0",    # Need to find minimum version that works
    "humanize>=0.5.1",    # Need to find minimum version that works
    "lxml>=4.2.5",    # Need to find minimum version that works
    "pandas>=0.23.4",    # Need to find minimum version that works
    "selenium>=3.141.0",    # Need to find minimum version that works
]

setup(
    name='django-temperature-monitor',
    version='0.0.0',
    packages=['temperature_monitor'],
    include_package_data=True,
    license='BSD License',
    keywords='temperature monitor humidity refrigerator freezer records',
    description='A Django app to simultaneously monitor multiple La Crosse Alerts sensors and keep an extended history of data points',
    long_description=(read('README.rst') + '\n\n' +
                      read('CHANGELOG.rst')),
    url='https://github.com/mfcovington/django-temperature-monitor',
    author='Michael F. Covington',
    author_email='mfcovington@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Documentation',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=install_requires,
)
