# Developers

---

## Project Organization

All of the source code is within the distribution `src`.

## Developer Setup

We prefer to do our development in PyCharm CE.

### Prerequisites

Python 3.7 or greater

### Setup

1. Fork `MoravianCollege/mirrulations` to your account.
2. `git clone <yourfork>`
3. `cd mirrulations`
4. `python3 -m venv .env`
5. `source .env/bin/activate/`
6. `pip install -r requirements.txt`
7. `pip install -e .`
8. 	`python setup.py install`
9. `python src/mirrulations/APIKeySetup.py`
10. `pytest`