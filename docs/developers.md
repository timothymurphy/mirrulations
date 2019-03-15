# Developers

---

## Project Organization

All of the source code is within the distribution `src` as various modules prefixed with `mirrulations`.

## Developer Setup

We prefer to do our development in PyCharm CE.

### Prerequisites

1. Python 3.7.2 or greater
2. Redis (if running a server)

### Setup

1. Get the repository:

		Fork MoravianCollege/mirrulations
		git clone https://github.com/your_username/mirrulations.git
		cd mirrulations

2. Set up your virtual environment:

		python3 -m venv .env
		source .env/bin/activate/
		pip install -e .

3. Run the tests:

		pytest

4. Open PyCharm CE.
