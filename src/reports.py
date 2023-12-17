import calendar
from collections import defaultdict
from datetime import timedelta

import reporttree
from parsing import *
from reporttree import tree
from utils import date_string

# ------------------------------------------------------------------------------------------------------------
# GOBAL
# ------------------------------------------------------------------------------------------------------------
BULLET = "  _*_ "  # todo, move lists to renderer ◯◦
BULLET2 = "  _o_ "  # todo, move lists to renderer ◯◦


# ------------------------------------------------------------------------------------------------------------
# REPORT FORMATTING:
# ------------------------------------------------------------------------------------------------------------

def task_display(task, url=None):
    task = task_join_external(task_split_internal(task))
    if url and len(url) > 0:
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

def report_tasks_at_state(df, postfixes, state, today):
    print("==="+ state if state else "NONE")
    df = completion_tasks(df, state, today)
    print(set(df.Task.to_list()))
    df = df[["Task", "Key", "Order"]]
    df = df.drop_duplicates().sort_values("Order")
    ret = ""
    for index, row in df.iterrows():
        k = f"[{row.Key}]" if row.Key else ""
        k = f"{k:10s}"
        postfixes = f"POSTFIX '{postfixes[row.Task]}'" if row.Task in postfixes else ""
        ret += f"{k}\t{row.Task}\t{postfixes}\n"
    return ret


def report_tasks(df, postfixes, today):
    ret = ""
    states = {"PENDING":"PENDING","OPEN":None,"STANDBY":"STANDBY","CLOSED":"DONE"}
    for state in states:
        tmp = report_tasks_at_state(df, postfixes, states[state], today)
        ret += "\n  * "+state+":\n" + tmp
    return ret


def report_completion_tasks(df, completion_value=None, today=None):
    df = completion_tasks(df, completion_value, today)
    ret = report1(df, groupby="Task", display_date=True, display_key=False, last_only="Task", sortby="Order",
                  ascending=True)
    return ret


def report_log(df, task):
    tmp = df[df.Key == task]
    if len(tmp) > 0:
        task = tmp.iloc[0].Task
    df = df[df.Task == task]
    ret = report1(df, groupby="Date", display_date=True, display_key=False, last_only=None, sortby="Date",
                  ascending=True, display_group_headers=False)
    return ret


def report_closed_tasks(df):
    global _now

    df = completion_tasks(df, "DONE", today=_now)
    ret = report1(df, groupby="Task", display_date=False, display_key=False, last_only="Task", sortby="Order",
                  ascending=True)
    report_span()
    return ret


def write_report_span(df, startdate, enddate):
    title, tree, updates = report_span(df, startdate, enddate)
    txt = reporttree.write_reporttree(tree, updates, BULLET, BULLET2)
    return title, txt


def report_this_week(df, date):
    startdate = date + timedelta(days=-date.weekday())
    enddate = startdate + timedelta(days=6)
    weekno = startdate.isocalendar()[1]
    datestr = f"{enddate.date().year} / {enddate.date().month} / {startdate.date().day}-{enddate.date().day}"

    title = f"This Week #{weekno}: {datestr}"
    _, txt = write_report_span(df, startdate, enddate)
    return title, txt


def report_last_week(df, date, weeks=1):
    startdate = date + timedelta(days=-date.weekday(), weeks=-weeks)
    enddate = startdate + timedelta(days=(7 * weeks) - 1)
    weekno = startdate.isocalendar()[1]
    datestr = f"{enddate.date().year} / {enddate.date().month} / {startdate.date().day}-{enddate.date().day}"

    if weeks == 1:
        title = f"Last Week #{weekno}: {datestr}"
    else:
        title = f"Last {weeks} Weeks: {datestr}"
    _, txt = write_report_span(df, startdate, enddate)
    return title, txt


def report_today(df, date):
    title = f"Today {date.date().isoformat()}:"
    _, txt = write_report_span(df, date, date)
    return title, txt


def report_last_day(df, date):
    weekday = date.weekday()
    if weekday > 0:
        startdate = date + timedelta(days=-1)
    else:
        startdate = date + timedelta(days=-3)
    title = calendar.day_name[startdate.weekday()]
    title = f"{title} {startdate.date().isoformat()}:"
    _, txt = write_report_span(df, startdate, startdate)
    return title, txt


def show_url(url):
    if not url or len(url) == 0:
        return ""
    return f" ([link]({url}))"


def report_span(df, startdate, enddate):
    if startdate == None and enddate == None:
        title = "SPAN: All"

    elif startdate == None:
        df = df[df.Date <= str(enddate.date())]
        title = f"SPAN: <= {enddate:%Y-%m-%d}\n\n"

    elif enddate == None:
        df = df[df.Date >= str(startdate.date())]
        title = f"SPAN: >= {startdate:%Y-%m-%d}\n\n"
    else:
        df = df[(df.Date >= str(startdate.date())) & (df.Date <= str(enddate.date()))]
        title = f"SPAN: {startdate:%Y-%m-%d} - {enddate:%Y-%m-%d}\n\n"

    tree, updates = _report(df)
    return title, tree, updates


def done(bool):
    return "  ✓" if bool else ""


def _report(df):
    tasktree = tree()
    updates = defaultdict(list)
    df = df.sort_values(["Order", "Task", "URL"])
    for r in df.itertuples():
        task_path = task_split_internal(r.Task)
        p = tasktree
        for t in task_path:
            if t not in p:
                p[t] = tree()
            p = p[t]
        p["_key"] = r.Task
        updates[r.Task].append(r.Update + done(r.Done))
    return tasktree, updates


# ------------------------------------------------------------------------------------------------------------
# FILTERS:
# ------------------------------------------------------------------------------------------------------------


def start_dates(data):
    df = data
    df = df.sort_values(by=["Date"]).groupby(["Task"]).head(1)
    return df


def end_dates(data):
    global _now
    return completion_tasks(data, "DONE", today=_now)


def completion_tasks(data, completion_value, today=None):
    df = data
    if today:
        df = df[(df.Date <= today)]
    df = df.sort_values(by=["Date"]).groupby(["Task"]).tail(1)
    if completion_value is None:
        return df[df.Done.isnull()]
    else:
        return df[(df.Done == completion_value)]
