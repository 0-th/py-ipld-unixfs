from enum import IntEnum
from dataclasses import dataclass
from typing import Literal, TypeAlias


class NodeType(IntEnum):
    """Types of UnixFS nodes."""
    Raw = 0
    Directory = 1
    File = 2
    Metadata = 3
    Symlink = 4
    HAMTShard = 5


int64: TypeAlias = int
fixed32: TypeAlias = int
uint64: TypeAlias = int
uint32: TypeAlias = int


@dataclass(frozen=True)
class MTime:
    """
    Represents modification time in seconds relative to the unix epoch
    1970-01-01T00:00:00Z.
    """
    secs: int
    nsecs: int | None = None


Mode: TypeAlias = int
"""
The mode is for persisting the file permissions in [numeric notation].
If unspecified this defaults to
- `0755` for directories/HAMT shards
- `0644` for all other types where applicable

The nine least significant bits represent `ugo-rwx`
The next three least significant bits represent setuid, setgid and the sticky bit.
The remaining 20 bits are reserved for future use, and are subject to change.
Spec implementations MUST handle bits they do not expect as follows: 
- For future-proofing the (de)serialization layer must preserve the entire
  `uint32` value during clone/copy operations, modifying only bit values that
   have a well defined meaning:
   `clonedValue = ( modifiedBits & 07777 ) | ( originalValue & 0xFFFFF000 )`
- Implementations of this spec MUST proactively mask off bits without a
  defined meaning in the implemented version of the spec:
  `interpretedValue = originalValue & 07777`


[numeric notation]:https://en.wikipedia.org/wiki/File-system_permissions#Numeric_notation

@see https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/sys_stat.h.html
"""


@dataclass(frozen=True)
class Metadata:
    mode: Mode | None = None
    mtime: MTime | None = None


@dataclass(frozen=True)
class SimpleFile:
    """
    Logical representation of a file that fits a single block.

    Note this is only semantically different from a `FileChunk` and your 
    interpretation SHOULD vary depending on where you encounter the node 
    (In root of the DAG or not).
    """
    content: bytes | bytearray
    type: Literal[NodeType.File] = NodeType.File
    layout: Literal["simple"] = "simple"
    metadata: Metadata | None = None


@dataclass(frozen=True)
class Raw:
    """
    Represents a UnixFS Raw node (a leaf node of the file DAG layout).

    This representation has been subsumed by `FileChunk` representation and
    is therefore marked as deprecated.

    UnixFS consumers are very likely to encounter nodes of this type, as of this
    writing JS & Go implementations can be configured to produce these nodes,
    in trickle DAG use this configuration.

    UnixFS producers are RECOMMENDED to either use `FileChunk` representation or
    better yet raw binary nodes (That is 0x55 multicodec) which will likely
    replace them in the future.

    See: https://github.com/multiformats/multicodec/blob/master/table.csv#L39

    Please note that in the wild Raw nodes are likely to come with other fields
    encoded but both encoder and decoder presented here will ignore them.

    Deprecated: Use FileChunk or raw binary nodes instead.
    """
    content: bytes  # Python's bytes is equivalent to Uint8Array
    type: Literal[NodeType.Raw] = NodeType.Raw  # This enforces the type at runtime
