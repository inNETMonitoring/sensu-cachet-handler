from setuptools import setup, find_packages
from os import path
from codecs import open

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name="sensu-cachet-handler",
      version="0.0.1",
      description="An application to publish your sensu check results to cachet",
      install_requires=[
          "cachet-client",
          "sensu-plugin"
      ],
      long_description=long_description,
      long_description_content_type="text/markdown",
      author="Michael Blättler",
      author_email="michael.blaettler@innetag.ch",
      packages=find_packages(),
      zip_safe=False,
      entry_points={
          "console_scripts": [
              "cachet_publisher=cachet_publisher.__main__:main",
              "cachet_metric=cachet_metric.__main__:main"
          ]}
      )
