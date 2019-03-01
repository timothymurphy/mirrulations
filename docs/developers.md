# Developers

---

## Project Organization

All of the source code is within the distribution `src` as a module named `mirrulations`.

## Developer Setup

We prefer to do our development in PyCharm CE.

### Prerequisites

1. Python 3.7 or greater

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

4. Run the tests:

		pytest

5. Open PyCharm CE.
