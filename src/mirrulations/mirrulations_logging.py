import logging

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(filename='mirrulations.log', format=FORMAT)
logger = logging.getLogger('mirrulations')
