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

		python setup.py install
		python src/mirrulations/APIKeySetup.py
		- IP: 0.0.0.0
		- Port:  8080
		- API Key:  [Get from here.](https://www.data.gov)

5. Run the tests:

		(in another terminal window) redis-server
		pytest

6. Open PyCharm CE.