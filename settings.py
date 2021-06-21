from JSONSource import JSONSource
from ExpandedWriter import ExpandedWriter
from os import cpu_count

INCLUDE_HEADER = True
INCLUDE_TITLE = False
DEFAULT_LANGUAGE = "en_core_web_sm"
NUM_WORKERS = cpu_count()
BATCH_SIZE = NUM_WORKERS
DETECT_LANGUAGE = False
TIME = True

WRITER = ExpandedWriter
DOCUMENT_SOURCE = JSONSource

STOP_POS_TAGS = ["VERB"]