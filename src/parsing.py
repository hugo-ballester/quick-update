import re
import pandas as pd
from datetime import datetime

import renderer
from utils import myassert, debug


TASK_SEPARATOR_INPUT = "::"  # TODO parametrise
DONE_KEYWORDS = ["(CLOSED)", "(.)"]
STANDBY_KEYWORDS = ["(STANDBY)", "(,)"]
DONE_OR_STANDBY_KEYWORDS = DONE_KEYWORDS + STANDBY_KEYWORDS
TODO_PREFIX = "#TODO "
TODO_CONT_PREFIX = "#- "

date_rex = re.compile("^#\\s*(\\d+)[ /-](\\d+)[ /-](\\d+)\\n?$")


def parse_date(line):
    new_date = None
    date_m = re.search(date_rex, line)
    if date_m:
        new_date = datetime.strptime(
            "-".join([date_m.group(x) for x in range(1, 4)]), "%Y-%m-%d"
        ).date()
    return new_date


def task_split_input(tasks):
    return re.split(f" *{TASK_SEPARATOR_INPUT} *", tasks)


def task_split_internal(tasks):
    return tasks.split(f"{TASK_SEPARATOR_INPUT}")


def task_join_internal(tasks):
    return TASK_SEPARATOR_INPUT.join(tasks)


def task_split_external(tasks):
    return tasks.split(" / ")


def task_join_external(tasks):
    return " / ".join(tasks)



# ------------------------------------------------------------------------------------------------------------
# IO:
# ------------------------------------------------------------------------------------------------------------

# ------------
# INIT PARSER:


# REGEX expressions:
regex_url = r"\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"

# TASK LINE DEFINITION:
done_exp = "|".join([re.escape(x) for x in DONE_OR_STANDBY_KEYWORDS])
done_exp = "(?P<done> " + done_exp + ")?"
line_parser_rex = re.compile(
    f"^(?P<task>[^][]+){TASK_SEPARATOR_INPUT}[ \t]+(?P<update>.+?){done_exp}$"
)  # need on-greedy +? so update does not swallow DONE

# TASK ALIAS DEFINITION:
# [Alias] Task::{ POSTFIX|postfixes|}{  ORDER:order}{ *url}

alias_rex = re.compile(
    f"(?i)^\\[(?P<key>[^]]+)?\\][ \t]+(?P<task>.+){TASK_SEPARATOR_INPUT}[ \t]*(?P<url>{regex_url})?[ \t]*(?:DESC<(?P<desc>[^>]+)>)?[ \t]*(?:POSTFIX<(?P<postfixes>[^>]+)>)?[ \t]*(?:ORDER<(?P<order>[^>]+)>)?[ \t]*(?P<update>.+?)?{done_exp}$"
)

url_shorthand_rex = re.compile(f"(?P<word>[^\\s]+):(?P<url>{regex_url})")

blank_rex = re.compile("^\\s*$")
doclines = re.compile("^###+")


def resolve_update(update):
    update = update.strip()
    update = url_shorthand_rex.sub("[\\1](\\2)", update)
    return update


def parse_line(line, aliases, urls, postfixes, order):
    '''
    Returns (task, update, done) if an update is encountered (aliases will not be resolved yet).
    Updates (aliases, urls, postfixes, order) if an alias is encountered
    :return: None or  (task, update, done)
    '''
    # PARSE

    ## shortcuts:
    line = re.sub(r"^([a-zA-Z]+):+ +", r"\1:: ", line)

    alias = alias_rex.search(line)
    if alias:
        d = alias.groupdict()
        task = task_join_internal(task_split_input(d["task"]))
        aliases[d["key"]] = task
        if "postfixes" in d and d["postfixes"]:
            postfixes[task] = d["postfixes"]
        if "url" in d and d["url"]:
            urls[task] = d["url"]
        if "order" in d and d["order"]:
            order[task] = d["order"]

        if "update" in d and d["update"]:
            line = f"{d['key']}:: {d['update']}"
        else:
            return None

    if line.startswith("["):  # bad alias line?
        raise SyntaxError(f"Could not parse task alias line: [{line}]")

    def _parse_update_line(line):
        rex = line_parser_rex.search(line)
        if not rex:
            raise SyntaxError
        d = rex.groupdict()
        tasklis = task_split_input(d["task"])
        task = task_join_internal(tasklis)
        done = None
        if d["done"]:
            dd = d["done"].strip()
            if dd in DONE_KEYWORDS:
                done = "DONE"
            elif dd in STANDBY_KEYWORDS:
                done = "STANDBY"
            else:
                myassert(False, f"UNKNOWN state VALUE: [{d['done']}]")
        update = resolve_update(d["update"])
        return task, update, done

    task, update, done = _parse_update_line(line)

    return task, update, done


def todo(todos):
    if len(todos) > 0:
        renderer.printAndCopy("\n".join(todos), "TODO")


def parse_file(string):
    date = None
    data = []
    todos = []
    aliases = {}
    urls = {}
    postfixes = {}
    order = {}

    lines = string.split("\n")

    # Check date order, and sort lines in date order:
    date_ascending, old_date, date1, date2 = (None, None, None, None)
    linenum = 0
    for line in lines:
        linenum += 1
        line = line.strip()
        date_m = parse_date(line)
        if date_m:
            if not date1:
                date1 = date_m
                continue
            if not date2:
                date2 = date_m
                date_ascending = date2 > date1
                old_date = date2
                continue
            else:

                if (date_ascending and old_date >= date_m) or (
                        not date_ascending and old_date <= date_m
                ):
                    myassert(
                        False,
                        f"PARSE ERROR (LINE: {linenum}) Dates can be incremental or decremental but not both!\nLINE: {line}",
                    )
                old_date = date_m

    # Parse updates
    linenum = 0
    doclines_on = False
    for line in lines:
        linenum += 1
        line = line.strip()

        if doclines.match(line):
            doclines_on = not doclines_on
            continue

        if doclines_on:
            continue

        if re.match(r'^#?TODO', line):
            todos.append(line)
            continue

        date_m = parse_date(line)
        if date_m:
            date = date_m
            continue

        if line.startswith("#") or blank_rex.match(line):
            continue

        try:
            res = parse_line(line, aliases, urls, postfixes, order)
        except SyntaxError:
            myassert(False, f"PARSE ERROR (LINE: {linenum}):\n{line}")
        if res:
            task, update, done = res
            if update:
                myassert(
                    date,
                    f"PARSE ERROR (LINE: {linenum}) No date line present before the first update!\nLINE: |{line}|"
                )

            data.append([date, task, update, done])
    DATE, TASK, UPDATE, DONE = (0, 1, 2, 3)


    # Resolve aliases as postfixes and format updates
    for datum in data:
        task = datum[TASK]
        tasklis = task_split_internal(task)
        key = tasklis[0]
        if key in aliases:
            tasklis[0] = aliases[key]
            task = datum[TASK] = task_join_internal(tasklis)
        if task in postfixes:
            POSTFIX = postfixes[task]
            if POSTFIX in DONE_KEYWORDS:
                datum[DONE] = "DONE"
            elif POSTFIX in STANDBY_KEYWORDS:
                datum[DONE] = "STANDBY"
            else:
                datum[UPDATE] += " " + POSTFIX

    df = pd.DataFrame(data, columns=["Date", "Task", "Update", "Done"])
    df.Date = pd.to_datetime(df.Date)

    # Set "pending" state
    pending_tasks = df[df.Update.str.contains(re.escape("(!)"))].Task.to_list()
    df.loc[df.Task.isin(pending_tasks), "Done"] = "PENDING"

    # add Keys (for display):
    task_to_key = {v: k for k, v in aliases.items()}
    df["Key"] = [
        task_to_key[task] if task in task_to_key else None for task in df.Task.tolist()
    ]
    df["Order"] = [
        order[task] + task if task in order else task for task in df.Task.tolist()
    ]
    df["URL"] = [urls[task] if task in urls else "" for task in df.Task.tolist()]


    # Check unused Task aliases
    used_tasks = set(df.Key.tolist())
    unused_aliases = [alias for alias in aliases if alias not in used_tasks]
    if unused_aliases:
        print("WARNING: UNUSED ALIASES: [" + ", ".join(unused_aliases)+"]")



    return df, todos, postfixes, date_ascending, aliases
