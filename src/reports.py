import subprocess
from datetime import timedelta, datetime


from parsing import *
from utils import date_string

# ------------------------------------------------------------------------------------------------------------
# GOBAL
# ------------------------------------------------------------------------------------------------------------
BULLET = "  _*_ " # todo, move lists to renderer ◯◦

# ------------------------------------------------------------------------------------------------------------
# REPORT FORMATTING:
# ------------------------------------------------------------------------------------------------------------

def task_display(task, url=None):
    task = task_join_external(task_split_internal(task))
    if url and len(url)>0:
        task = f"[{task}]({url})"
    return task

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
    prefx = "  " * (level + 1) + BULLET
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
            ret += BULLET + str(name) + "\n" + tmp
        else:
            ret += tmp

    return ret



# ------------------------------------------------------------------------------------------------------------
# REPORTS:
# ------------------------------------------------------------------------------------------------------------

def report_tasks(df, posfix):
    #    df=df[df.Key.notnull()]
    df = df[["Task", "Key", "Order"]]
    df = df.drop_duplicates().sort_values("Order")
    ret =  ""
    for index, row in df.iterrows():
        k = f"[{row.Key}]" if row.Key else ""
        k = f"{k:10s}"
        posfix = f"POSFIX '{posfix[row.Task]}'" if row.Task in posfix else ""
        ret += f"{k}\t{row.Task}\t{posfix}\n"
    return ret


def report_open_tasks(df):
    df = open_tasks(df)
    ret = report1(df, groupby="Task", display_date=True, display_key=False, last_only="Task", sortby="Order",
                   ascending=True)
    return ret


def report_log(df, task):
    tmp = df[df.Key==task]
    if len(tmp)>0:
        task=tmp.iloc[0].Task
    df = df[df.Task == task]
    ret = report1(df, groupby="Date", display_date=True, display_key=False, last_only=None, sortby="Date",
                   ascending=True, display_group_headers=False)
    return ret


def report_closed_tasks(df):
    global _now
    df = closed_tasks(df, _now)
    ret = report1(df, groupby="Task", display_date=False, display_key=False, last_only="Task", sortby="Order",
                   ascending=True)
    report_span()
    return ret


def report_last_week(df, date):
    startdate = date + timedelta(days=-date.weekday(), weeks=-1)
    enddate = startdate + timedelta(days=6)
    weekno = startdate.isocalendar()[1]
    datestr = f"{enddate.date().year} / {enddate.date().month} / {startdate.date().day}-{enddate.date().day}"

    title = f"Last Week #{weekno}: {datestr}"
    _, txt = report_span(df, startdate, enddate)
    return title,txt

def report_today(df, date):
    title = f"Today ({date.date().isoformat()}):"
    _, txt = report_span(df, date, date)
    return title, txt

def report_last_day(df, date):
    weekday = date.weekday()
    if weekday>0:
        startdate = date + timedelta(days=-1)
    else:
        startdate = date + timedelta(days=-3)

    title = f"Yesterday ({startdate.date().isoformat()}):"
    _, txt = report_span(df, startdate, startdate)
    return title, txt

def report_this_week(df, date):
    startdate = date + timedelta(days=-date.weekday())
    enddate = startdate + timedelta(days=6)
    weekno = startdate.isocalendar()[1]
    datestr = f"{enddate.date().year} / {enddate.date().month} / {startdate.date().day}-{enddate.date().day}"

    title = f"This Week #{weekno}: {datestr}"
    _, txt = report_span(df, startdate, enddate, force_subbullets=True)
    return title,txt

def show_url(url):
    if not url or len(url)==0:
        return ""
    return f" ([link]({url}))"

def report_span(df, startdate, enddate, force_subbullets=False):
    if startdate==None and enddate==None:
        title = "SPAN: All"

    elif startdate==None:
        df = df[df.Date <= str(enddate.date())]
        title = f"SPAN: <= {enddate:%Y-%m-%d}\n\n"

    elif enddate == None:
        df = df[df.Date >= str(startdate.date())]
        title = f"SPAN: >= {startdate:%Y-%m-%d}\n\n"
    else:
        df = df[(df.Date >= str(startdate.date())) & (df.Date <= str(enddate.date()))]
        title = f"SPAN: {startdate:%Y-%m-%d} - {enddate:%Y-%m-%d}\n\n"

    txt = report(df, force_subbullets=force_subbullets)
    return title, txt

def done(bool):
    return "  ✓" if bool else ""

def report(df, force_subbullets=False):
    global BULLET
    ret = ""
    df = df.groupby(["Order", "Task", "URL"])  # groupby order first to preserve right order
    SEP = " : "
    for (_, task, url), group in df:
        ret += BULLET + task_display(task, url) + SEP
        if group.shape[0] > 1 or force_subbullets:
            ret += "\n"
            prefx2 = "  " + BULLET
            for index, row in group.iterrows():
                ret += f"{prefx2}{row.Update}{done(row.Done)}\n"
        else:
            row = [r for i, r in group.iterrows()]
            ret += f"{row[0].Update}\n"

    return ret


# ------------------------------------------------------------------------------------------------------------
# FILTERS:
# ------------------------------------------------------------------------------------------------------------


def start_dates(data):
    df = data
    df = df.sort_values(by=["Date"]).groupby(["Task"]).head(1)
    return df


def end_dates(data):
    global _now
    return closed_tasks(data, _now)


def open_tasks(data, today=None):
    df = data
    if today:
        df = df[(df["Date"] <= today)]
    df = df.sort_values(by=["Date"]).groupby(["Task"]).tail(1)
    df = df[(df["Done"] == False)]
    return df


def closed_tasks(data, today=None):
    df = data
    if today:
        df = df[(df["Date"] <= today)]
    df = df.sort_values(by=["Date"]).groupby(["Task"]).tail(1)
    df = df[(df["Done"])]
    return df



