import subprocess
from datetime import datetime
import sys

from dateutil.relativedelta import relativedelta



def date_string(dt, now=datetime.now()):
    if not dt:
        return ""
    rd = relativedelta(now, dt)
    if rd.years or rd.months:
        months = 12 * rd.years + rd.months
        return f"{months:.0f}m"
    elif rd.days > 7:
        weeks = rd.days / 7
        return f"{weeks:.0f}w"
    else:
        return f"{rd.days:.0f}d"

def myassert(test, msg):
    if not test:
        sys.exit(f"ERROR (QUITTING): " + msg)


def debug(string, title=""):
    print(f"--- DEBUG: {title}---")
    print(str(string))
    print("------------------------------------------------------")


