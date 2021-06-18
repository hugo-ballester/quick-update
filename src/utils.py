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


# == DISPLAY ===========================================================================================
def bold(string):
    BOLD = "\033[1m"
    END = "\033[0m"
    return BOLD + string + END

def debug(string, title=""):
    print(f"--- DEBUG: {title}---")
    print(str(string))
    print("------------------------------------------------------")

terminal_cols = 80
try:
    _, terminal_cols = subprocess.check_output(["stty", "size"]).decode().split()
except:
    pass
headline1 = "=" * int(terminal_cols)
headline2 = "_" * int(terminal_cols)
def title_str(string):
    return bold(headline2 + "\n" + string)
