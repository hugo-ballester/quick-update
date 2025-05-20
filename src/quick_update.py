"""
QuickUpdate
Hugo Zaragoza, 2020.

see README.md for usage documentation


"""
import argparse
import glob
import os
import shutil
import sys
from datetime import datetime

import pandas as pd
from loguru import logger

import renderer
import reports
from parsing import *
from utils import myassert, debug

# ------------------------------------------------------------------------------------------------------------
# DESIGN
# ------------------------------------------------------------------------------------------------------------
app_name = "QuickUpdate"
version_name = "v1.1"
err_pre = "INPUT DATA ERROR:"

pd.set_option('display.max_columns', None)


# ------------------------------------------------------------------------------------------------------------
# FILE MANIPULATION
# ------------------------------------------------------------------------------------------------------------

def add_date_to_file(file, now):
    '''
    Rewrite file adding now's date entry.
    '''
    # Find out if ascending or descending:
    date_ascending = None
    date = None
    for line in open(file, "r"):
        d = re.search(date_rex, line)
        if d:
            d = datetime.strptime("-".join([d.group(x) for x in range(1, 4)]), "%Y-%m-%d")
            if date is None:
                date = d
            else:
                date_ascending = d > date
                break
    if date_ascending is None:
        return

    # Write new File:
    date_str = f"# {now.strftime('%Y-%m-%d')}\n\n\n"
    newfile = ""
    today_inserted = False
    for line in open(file, "r"):
        d = re.search(date_rex, line)
        if not today_inserted and d:
            d = datetime.strptime("-".join([d.group(x) for x in range(1, 4)]), "%Y-%m-%d").date()
            debug(f"1: {now.date()} - {d}")
            if d == now.date():
                today_inserted = True  # not needed
            else:
                if d and not date_ascending:
                    newfile += date_str
                    today_inserted = True
        newfile += line
    if not today_inserted:
        newfile += date_str
        today_inserted = True

    shutil.copyfile(file, f"{file}.old")

    with open(file, "w") as text_file:
        text_file.write(newfile)


# ------------------------------------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------------------------------------


_now = datetime.now()


def error_and_quit(txt):
    print(txt)
    sys.exit(1)


def main():

    with open('README.md', 'r') as file:
        readme_content = file.read()


#    print(readme_content)
#    sys.exit()

    commands_list = ["o[pen]", "pending", "standby", "closed", "y[esterday]", "today", "thisweek", "[last]week",
                     "<k>w[eeks]",
                     "span <date-start> <date-end>", "tasks", "tr/tasks_recent", "todo"]

    ap = argparse.ArgumentParser(
        description=f"QuickUpdate {version_name}: https://github.com/hugozaragoza/quick-update\n\n"+readme_content,
        formatter_class=argparse.RawTextHelpFormatter
        )

    ap.add_argument(
        "commands",
        type=str,
        nargs="+",
        help=", ".join(commands_list),
    )

    ap.add_argument(
        "-f",
        "--update_file",
        required=True,
        default=None,
        help="Update file or file pattern (date order should be consistent)",
    )
    ap.add_argument(
        "--now",
        required=False,
        help="Use a different date for today (for reports relative to today). Use format %%Y-%%m-%%d",
    )
    ap.add_argument(
        "--task",
        required=False,
        help="Filter to only this task (or task alias)",
    )
    ap.add_argument(
        "--filter",
        required=False,
        help="Filter to any task or update containing this substring",
    )
    args = vars(ap.parse_args())
    files = args["update_file"]

    if (args['now']):
        global _now
        _now = datetime.strptime(args['now'], '%Y-%m-%d')
        print("WARNING: NOW is set to " + str(_now))

    if "edit" in args["commands"]:
        add_date_to_file(files, _now)
        os.system(f"open {files}")
        args["commands"].remove("edit")

    if len(args["commands"]) == 0:
        return

    print(f"FILES: {files}")
    file_content = ''
    files_matched = sorted(glob.glob(files),reverse=True)
    if not files_matched:
        error_and_quit(f"\nNo files found of: {files}")

    for filename in files_matched:
        # print(f"  FILES: {filename}")
        with open(filename, "r") as _file:
            file_content += _file.read()+"\n"
    df, todos, postfixes, date_ascending, aliases = parse_file(file_content)

    if args['task']:
        task = args['task']
        if task in aliases:
            task = aliases[task]
        task2 = task_join_internal(task_split_external(task))
        df = df[(df.Task == task) | (df.Task == task2)]
        print(f"FILTERING BY task==[{task}] ({len(df)}  rows)")

    if args['filter']:
        df = df[df.Update.str.contains(re.escape(args['filter']))]
        print(f"FILTERING BY search string [{args['filter']}] ({len(df)}  rows)")

    args_to_skip = 0
    for i in range(len(args["commands"])):
        if args_to_skip > 0:
            args_to_skip -= 1
            continue

        command = args["commands"][i]
        m_k = re.fullmatch("(?P<k>[0-9]+)w(?:eeks)?", command)

        if command == "all":
            title, txt = reports.write_report_span(df, None, None)
            renderer.printAndCopy(txt, title=title)
            todo(todos)

        elif command == "pending":
            df = df[df.Update.str.contains(re.escape("(!)"))]
            title, txt = reports.write_report_span(df, None, None)
            renderer.printAndCopy(txt, title=title)

        elif command == "pending":
            title, txt = reports.write_report_span(df, None, None)
            renderer.printAndCopy(txt, title=title)

        elif command == "thisweek":
            title, txt = reports.report_this_week(df, _now)
            renderer.printAndCopy(txt, title=title)
            todo(todos)

        elif (command == "lastweek") or (command == "week") or (command == "w"):
            title, txt = reports.report_last_week(df, _now)
            renderer.printAndCopy(txt, title=title)
            todo(todos)

        elif m_k:
            k = int(m_k.groupdict()["k"])
            title, txt = reports.report_last_week(df, _now, weeks=k)
            renderer.printAndCopy(txt, title=title)
            todo(todos)

        elif (command == "yesterday") or (command == "y"):
            title, txt = reports.report_last_day(df, _now)
            renderer.printAndCopy(txt, title=title)
            todo(todos)

        elif (command == "today"):
            title, txt = reports.report_today(df, _now)
            renderer.printAndCopy(txt, title=title)
            todo(todos)

        elif command == "span":
            startdate = datetime.strptime(args["commands"][i + 1], '%Y-%m-%d')
            enddate = datetime.strptime(args["commands"][i + 2], '%Y-%m-%d')
            title, txt = reports.write_report_span(df, startdate, enddate)
            renderer.printAndCopy(txt, title=title)
            todo(todos)
            args_to_skip += 2

        elif (command == "open") or (command == "o"):
            renderer.printAndCopy(reports.report_completion_tasks(df, None), "OPEN TASKS")
            todo(todos)

        elif command == "standby":
            renderer.printAndCopy(reports.report_completion_tasks(df, "STANDBY"), "STANDBY TASKS")
            todo(todos)

        elif command == "closed":
            renderer.printAndCopy(reports.report_completion_tasks(df, "DONE"), "CLOSED TASKS")

        elif command == "tasks":
            renderer.printAndCopy(reports.report_tasks(df, postfixes, _now), "TASKS")

        elif command == "tasks_recent" or command=="tr":
            renderer.printAndCopy(reports.report_tasks(df, postfixes, _now, 10), "TASKS")

        elif command == "todo":
            renderer.printAndCopy("\n".join(todos), "TODO")

        else:
            print(
                f"UNKNOWN COMMAND [{command}]. DEFINED COMMANDS: {', '.join(commands_list)}"
            )


if __name__ == "__main__":
    main()
