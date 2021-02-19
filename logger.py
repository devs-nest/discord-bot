#
# Author: vaibhavgupta353@gmail.com
#
# Example:
#
#   from log import *
#   import log
#
#   log.initialize("foo.log")
#   INFO("A log message")




__all__ = [ "initialize", "DEBUG", "INFO", "WARNING", "ERROR", "FATAL"]

import logging
import os
import sys

class _DiscordLogger(object):
  """
  The method logging.getLogger already has singleton behavior. But we need to
  prevent adding handles multiple times to the same logger. Hence this class is
  used to help store the logger and remember that we already initialized.
  """
  _discord_logger = None
  _min_log_level = logging.INFO

DATA_FORMAT_STR = "%Y-%m-%d %H:%M:%S"
LOG_FORMAT_STR = "%(asctime)s,%(msecs)03dZ %(levelname)s %(file_line)s %(message)s"

def initialize(logfile=None):
  """
  Initialize logging subsystem to log to the file 'logfile'.

  If 'logfile' is None and environment variable DISCORD_LOG_DIR is unset, then
  log messages go to stdout. If 'logfile' is None and the DISCORD_LOG_DIR
  environment variable has a path to a directory, then log file is created in
  that directory with the current script name and a ".log" extension.
  """
  if _DiscordLogger._discord_logger:
    # Initialization already done.
    return _DiscordLogger._discord_logger

  # Set up log_handler to either a file or stderr.
  log_handler = None
  if not logfile and os.environ.has_key("DISCORD_LOG_DIR") and \
      os.path.isdir(os.environ["DISCORD_LOG_DIR"]):

    logfile = os.path.join(
      os.environ["DISCORD_LOG_DIR"],
      os.path.basename(os.path.splitext(sys.argv[0])[0]) + ".log")

  if logfile:
    log_handler = logging.FileHandler(filename=logfile)
  else:
    log_handler = logging.StreamHandler() # Defaults to stderr.

  datefmt = DATA_FORMAT_STR


  formatter = logging.Formatter(LOG_FORMAT_STR, datefmt=datefmt)
  # Set logging to UTC.
  # formatter.converter = time.gmtime
  log_handler.setFormatter(formatter)

  _DiscordLogger._discord_logger = logging.getLogger("logger")
  _DiscordLogger._discord_logger.addHandler(log_handler)
  # Propagate ensures messages don't get passed to parent loggers till root.
  _DiscordLogger._discord_logger.propagate = False
  _DiscordLogger._logfile = logfile
  update_min_log_level()
  return _DiscordLogger._discord_logger

def DEBUG(msg, **kwargs):
  if _DiscordLogger._min_log_level > logging.DEBUG:
    return
  if _DiscordLogger._discord_logger:
    _DiscordLogger._discord_logger.debug(msg)
  else:
    logging.debug(msg, extra=kwargs)

def INFO(msg, **kwargs):
  if _DiscordLogger._min_log_level > logging.INFO:
    return
  if _DiscordLogger._discord_logger:
    _DiscordLogger._discord_logger.info(msg)
  else:
    logging.info(msg, extra=kwargs)

def WARNING(msg, **kwargs):
  if _DiscordLogger._min_log_level > logging.WARNING:
    return
  if _DiscordLogger._discord_logger:
    _DiscordLogger._discord_logger.warning(msg, extra=kwargs)
  else:
    logging.warning(msg, extra=kwargs)

def ERROR(msg, **kwargs):
  if _DiscordLogger._min_log_level > logging.ERROR:
    return
  if _DiscordLogger._discord_logger:
    _DiscordLogger._discord_logger.error(msg, extra=kwargs)
  else:
    logging.error(msg, extra=kwargs)

def FATAL(msg, **kwargs):
  if _DiscordLogger._discord_logger:
    _DiscordLogger._discord_logger.critical(msg, extra=kwargs)
  else:
    logging.critical(msg, extra=kwargs)

  logging.shutdown()
  os._exit(1)

def update_min_log_level(min_log_level=logging.INFO):
  """
  Update logger level to minimum log level
  """
  if _DiscordLogger._discord_logger:
    _DiscordLogger._discord_logger.setLevel(min_log_level)
  _DiscordLogger._min_log_level = min_log_level
