import logging

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(filename='mirrulations.log', format=FORMAT, level=logging.INFO)
logger = logging.getLogger('mirrulations')
