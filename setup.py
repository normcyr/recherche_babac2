from setuptools import setup

setup(
    name='Recherche Babac2',
    version='0.0.1',
    packages=['recherche_babac2'],
    entry_points={
        'console_scripts': ['recherche_babac2=recherche_babac2.recherche_babac2:main'],
    },
    install_requires=[
        'python-dotenv',
        'bs4',
        'requests',
        'lxml',
    ],
    zip_safe=False,
    include_package_data=True,
)
