from enum import Enum
class UnixPermission(Enum):
    READ = 1
    WRITE = 2
    EXECUTE = 4
    NONE = 0
    READ_WRITE = READ + WRITE
    READ_EXECUTE = READ + EXECUTE
    WRITE_EXECUTE = WRITE + EXECUTE
    ALL = READ + WRITE + EXECUTE


unix_permission_list = (
    UnixPermission.READ.value,
    UnixPermission.WRITE.value,
    UnixPermission.EXECUTE.value,
    UnixPermission.NONE.value,
    UnixPermission.READ_WRITE.value,
    UnixPermission.READ_EXECUTE.value,
    UnixPermission.WRITE_EXECUTE.value,
    UnixPermission.ALL.value
)