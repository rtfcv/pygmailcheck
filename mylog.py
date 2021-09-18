import time
import logging
import logging.handlers

__doc__ = """ Simple Wrapper for Logging
"""


def log():
    """ Dummy Function
    """


def enableLog(fname, print=True):
    """Enable Logging
    Parameter:
    fname: Path of Logfile
    """
    global log
    _log = logging.getLogger()
    _log.addHandler(logging.handlers.RotatingFileHandler(fname))
    _log.setLevel(logging.INFO)
    _log.info(time.ctime() + ': ' + 'started logging')

    def log(str, print=print):
        """Write to Logfile
        Log Level is Info for now
        Parameter:
        str: What to Write to the log
        """
        __str = time.ctime() + ': ' + str
        _log.info(__str)
        if print:
            print(__str)


def disableLog():
    global log

    def log(str, print=True):
        """ Dummy Function
        """
        pass
