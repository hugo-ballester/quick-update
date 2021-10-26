from datetime import timedelta, datetime

from quick_update import open_tasks, closed_tasks, task_display, _now
from utils import title_str, date_string



design_bullet = "  * "

# ------------------------------------------------------------------------------------------------------------
# REPORT FORMATTING:
# ------------------------------------------------------------------------------------------------------------

def format_line(
        key,
        task,
        update="",
        done=False,
        date=None,
        level=0,
        display_key=True,
        display_done=False,
        url=None
):
    if display_key:
        key = f"[{key}]" if key else " "
        key = f"{key:7}"
    else:
        key = ""
    task = f"{task_display(task, url):30}\t" if task else ""
    ds = ''
    if date:
        ds = '(' + date_string(date) + ')'
        ds = f" {ds:s}"
    update = f": {update}" if update else ""
    prefx = "  " * (level + 1) + design_bullet
    done = "" if not display_done else " (DONE)" if done else " (...)"
    l = f"{prefx}{key}{task}{update}{done}{ds}\n"

    return l


def report1(
        df,
        groupby,
        display_key=True,
        display_done=False,
        display_date=False,
        last_only=None,
        sortby="Date",
        ascending=False,
        display_group_headers=True
):
    ret = ""
    if last_only:
        df = df.sort_values("Date").groupby(last_only).tail(1)
    df = df.sort_values(sortby, ascending=ascending)
    df = df.groupby(groupby, sort=False)

    for name, group in df:
        tmp = ""
        nrows = 0
        for index, row in group.iterrows():
            tmp += format_line(
                row.Key,
                row.Task,
                row.Update,
                date=row.Date if display_date else None,
                done=row.Done,
                level=1,
                display_key=display_key,
                display_done=display_done,
                url=row.URL
            )
            nrows += 1

        if display_group_headers and nrows > 1:
            ret += design_bullet + str(name) + "\n" + tmp
        else:
            ret += tmp

    return ret



# ------------------------------------------------------------------------------------------------------------
# REPORTS:
# ------------------------------------------------------------------------------------------------------------

def report_tasks(df, posfix, title="TASKS DEFINED:"):
    #    df=df[df.Key.notnull()]
    df = df[["Task", "Key", "Order"]]
    df = df.drop_duplicates().sort_values("Order")
    ret = title_str(title) + "\n"
    for index, row in df.iterrows():
        k = f"[{row.Key}]" if row.Key else ""
        k = f"{k:10s}"
        posfix = f"POSFIX '{posfix[row.Task]}'" if row.Task in posfix else ""
        ret += f"{k}\t{row.Task}\t{posfix}\n"
    return ret


def report_open_tasks(df, title="OPEN TASKS:"):
    df = open_tasks(df)
    ret = title_str(title) + "\n"

    ret += report1(df, groupby="Task", display_date=True, display_key=False, last_only="Task", sortby="Order",
                   ascending=True)
    return ret


def report_log(df, task, title="LOG:"):
    tmp = df[df.Key==task]
    if len(tmp)>0:
        task=tmp.iloc[0].Task
    df = df[df.Task == task]
    ret = title_str(title) + "\n"
    ret += report1(df, groupby="Date", display_date=True, display_key=False, last_only=None, sortby="Date",
                   ascending=True, display_group_headers=False)
    return ret


def report_closed_tasks(df, title="CLOSED TASKS:"):
    df = closed_tasks(df)
    ret = title_str(title) + "\n"
    ret += report1(df, groupby="Task", display_date=False, display_key=False, last_only="Task", sortby="Order",
                   ascending=True)
    return ret


def report_last_week(df):
    date = _now
    startdate = date + timedelta(days=-date.weekday(), weeks=-1)
    enddate = startdate + timedelta(days=6)
    weekno = startdate.isocalendar()[1]
    datestr = f"{enddate.date().year} / {enddate.date().month} / {startdate.date().day}-{enddate.date().day}"

    ret = title_str(f"Last Week #{weekno}: {datestr}\n\n")
    ret += report_span(df, startdate, enddate)
    return ret


def report_last_day(df):
    date = _now
    weekday = date.weekday()
    if weekday>0:
        startdate = date + timedelta(days=-1)
    else:
        startdate = date + timedelta(days=-3)

    ret = title_str(f"Yesterday: {startdate.date().isoformat()}\n\n")
    ret += report_span(df, startdate, startdate)
    return ret

def report_this_week(df):
    date = _now
    startdate = date + timedelta(days=-date.weekday())
    enddate = startdate + timedelta(days=6)
    weekno = startdate.isocalendar()[1]
    datestr = f"{enddate.date().year} / {enddate.date().month} / {startdate.date().day}-{enddate.date().day}"

    ret = title_str(f"This Week #{weekno}: {datestr}\n\n")
    ret += report_span(df, startdate, enddate)
    return ret

def show_url(url):
    if not url or len(url)==0:
        return ""
    return f" ([link]({url}))"

def report_span(df, startdate, enddate):
    df = df[(df.Date >= str(startdate.date())) & (df.Date <= str(enddate.date()))]
    ret = ""
    df = df.groupby(["Order", "Task", "URL"])  # groupby order first to preserve right order
    SEP = " : "
    level = 0
    prefx = "  " * (level + 1) + design_bullet
    for (_, task, url), group in df:
        ret += prefx + task_display(task, url) + SEP
        if group.shape[0] > 1:
            ret += "\n"
            for index, row in group.iterrows():
                ret += f"{row.Update}\n"
        else:
            row = [r for i, r in group.iterrows()]
            ret += row[0].Update + f"\n"

    return ret


def report_last_days(df):
    ret = title_str("LAST TASKS") + "\n"
    for i in range(0, 3):
        date = _now + timedelta(days=-i)
        dft = df[(df.Date == str(date.date()))]
        datestr = f"{date.date().year} / {date.date().month} / {date.date().day}"
        ret += f"Day {datestr}\n"
        ret += report1(
            dft, "Task", display_key=False, display_done=True, last_only=None
        )
    return ret


def show_day(df, offset, title_prefix=""):
    start_date = datetime.strftime(_now - timedelta(offset), "%Y-%m-%d")
    end_date = datetime.strftime(_now + timedelta(1), "%Y-%m-%d")
    title = f"{title_prefix}{start_date} - {end_date}:"

    mask = (df["Date"] >= start_date) & (df["Date"] <= end_date)
    df = df[mask]
    print(title_str(title))
    for index, row in df.iterrows():
        print(format_line(row.Key, row.Task, row.Update, row.Date, url=row.URL))

