from collections import namedtuple
from time import gmtime, strftime

FormattedTimeObject = namedtuple(
    'FormattedTimeObject',
    ['tm_year', 'tm_mon', 'tm_mday', 'tm_hour', 'tm_min', 'tm_sec', 'tm_wday', 'tm_yday', 'tm_isdst',
     's_date', 's_dow', 's_time']
)


def get_time():

    t_struct = gmtime()

    _to = FormattedTimeObject(
        t_struct.tm_year,
        t_struct.tm_mon,
        t_struct.tm_mday,
        t_struct.tm_hour,
        t_struct.tm_min,
        t_struct.tm_sec,
        t_struct.tm_wday,
        t_struct.tm_yday,
        t_struct.tm_isdst,
        strftime('%Y/%m/%d', t_struct),
        strftime('%A', t_struct),
        strftime('%H:%M', t_struct)
    )
    return _to

def utc_tuple():
     return gmtime().tm_hour, gmtime().tm_min
