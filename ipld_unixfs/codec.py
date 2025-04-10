from logging import getLogger

import ipld_dag_pb
from unixfs import Mode, NodeType, Raw, SimpleFile, Metadata
from gen.unixfs_pb2 import Data

logger = getLogger(__name__)

EMPTY = ()  # read-only tuple
EMPTY_BUFFER = bytearray()

BLANK = ()
DEFAULT_FILE_MODE = 0o644  # Python uses 0o prefix for octal literals
DEFAULT_DIRECTORY_MODE = 0o755

code = ipld_dag_pb.code
name = "UnixFS"

def encode_pb(data: Data, links: list[ipld_dag_pb.PBLink]) -> memoryview[int]:
    logger.debug({"data": data, "links": links})
    return ipld_dag_pb.encode(
        # We run through prepare as links need to be sorted by name which it will do
        ipld_dag_pb.prepare(
            {
                "data": data.SerializeToString(),
                "links": links
            }
        )
    )


def create_raw(content: bytes) -> Raw:
    return Raw(content)


def decode_mode(mode: Mode) -> Mode:
    return (mode & 0xfff) | (mode & 0xfffff000)


def decode_metadata(data: Metadata | None) -> Metadata | None:
    if data is None:
        return Metadata()
    else:
        ...


def create_simple_file(content: bytes | bytearray, metadata: Metadata) -> SimpleFile:
    return SimpleFile(type=NodeType.File, layout="simple", content=content, metadata=decode_metadata(metadata))


def create_empty_file(metadata: Metadata):
    create_simple_file(content=EMPTY_BUFFER, metadata=metadata)
