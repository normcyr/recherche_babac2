# Recherche Babac2

a sopel module to search the Cycle Babac catalogue

## Installation

1. Clone the repository


```bash
git clone https://github.com/normcyr/recherche_babac2
```

2. Create a Python virutal environment using `virtualenv`

```bash
cd recherche_babac2
virtualenv -p python3 venv
source venv/bin/activate
```

3. Install the requirements


```bash
pip install -r requirements.txt
```

## Setup the configuration file


```bash
cp config.example.yml config.yml
```

Then edit the `config.yml` file (**eg** `nano config.yml`) to include the proper credentials to log in to the Cycle Babac website.

## Perform a search

Launch the search with the following command:


```bash
python recherche_babac2.py search text
```

For example:

```bash
python recherche_babac2.py training wheels
```

or, using a catalogue number:

```bash
python recherche_babac2.py 22-150
```
