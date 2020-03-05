from setuptools import setup


def readme():
    with open("README.md", "r") as f:
        return f.read()


version = {}
with open("recherche_babac2/_version.py", "r") as fp:
    exec(fp.read(), version)


setup(
    name="Recherche Babac2",
    version=version["__version__"],
    description="A Python3 module to search the Cycle Babac catalogue and return description, price and availability.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Topic :: Office/Business :: Financial",
    ],
    keywords="bicycle babac parts repair diy",
    url="http://github.com/normcyr/recherche_babac2",
    author="Normand Cyr",
    author_email="norm@normandcyr.com",
    license="GNU GPLv3",
    packages=["recherche_babac2"],
    entry_points={
        "console_scripts": ["recherche_babac2=recherche_babac2.recherche_babac2:main"],
    },
    install_requires=["bs4", "requests", "lxml", "pyyaml",],
    zip_safe=False,
    include_package_data=True,
    python_requires=">=3.5",
)
