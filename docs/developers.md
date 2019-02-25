# Developers

---

## Project Organization

All of the source code is within the distribution `src` as a module named `mirrulations`.

## Developer Setup

We prefer to do our development in PyCharm CE.

### Prerequisites

1. Python 3.7 or greater
2. Redis-server

### Setup

1. Get the repository:

		Fork MoravianCollege/mirrulations
		git clone https://github.com/your_username/mirrulations.git
		cd mirrulations

2. Set up your virtual environment:

		python3 -m venv .env
		source .env/bin/activate/

3. Install packages:

		pip install -r requirements.txt
		pip install -e .

4. Run the preliminary files:

		python src/mirrulations/config_setup.py
		- IP:  0.0.0.0
		- Port:  8080
		- API Key:  Get from https://regulationsgov.github.io/developers/

5. Run the tests:

		(in another terminal window) redis-server
		pytest

6. Open PyCharm CE.
