# Developers

---

## Project Organization

All of the source code is within the distribution `src` as a module named `mirrulations`.

## Developer Setup

We prefer to do our development in PyCharm CE.

### Prerequisites

Python 3.7 or greater

### Setup

1. Get the repository:
	1. Fork `MoravianCollege/mirrulations`
	2. `git clone <yourforkurl>.git`
	3. `cd mirrulations`
2. Set up your virtual environment:
	1. `python3 -m venv .env`
	2. `source .env/bin/activate/`
3. Install packages:
	1. `pip install -r requirements.txt`
	2. `pip install -e .`
4. Run the preliminary files:
	1. `python setup.py install`
	2. `python src/mirrulations/APIKeySetup.py`
		* IP: 10.76.100.34
		* Port:  8080
		* API Key:  Ask someone!
5. Run the tests:
	1. In another terminal window, `redis-server`
	2. `pytest`
6. Open PyCharm CE.

At this moment, ignore the remaining three errors.
We're working on that.