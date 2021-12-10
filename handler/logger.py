import logging

logger = logging.getLogger("pci-handler")

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARN)  # for some reason changing this to INFO or DEBUG still doesn't show below WARN
console_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s"))
logger.addHandler(console_handler)
