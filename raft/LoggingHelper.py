import logging

def get_logger(module_name: str) -> logging.Logger:
  formatter = logging.Formatter(fmt="%(asctime)s [%(levelname)s] %(module)s - %(message)s")
  handler = logging.StreamHandler()
  handler.setFormatter(formatter)
  logger = logging.getLogger(module_name)
  logger.setLevel(logging.INFO)
  logger.addHandler(handler)
  return logger

