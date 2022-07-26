import re
from collections import defaultdict

import parsing
import utils
from utils import tab


def tree():
    """The report task structure tree. Each level contains a _key value with the full string path as well as any
    subtasks. Updates are stores separtedly"""
    return defaultdict(tree)


def format_task(str):
    bold_str = "\033[1m"
    end_str = "\033[0m"
    tasks = [utils.upper_first(x) for x in parsing.task_split_internal(str)]
    task = parsing.task_join_internal(tasks)
    return bold_str + task + end_str


def format_update(update):
    if not re.match("[.!?]", update[-1]):
        update += "."
    return utils.upper_first(update)


def depth_first_report(tree, updates, bullet1, bullet2, depth=0):
    ret = ""
    if "_key" in tree:
        key = tree["_key"]
        h = f"{tab(depth)}{bullet2}"
        ret += h + ("\n" + h).join([format_update(x) for x in updates[key]]) + "\n"

    for k, v in tree.items():
        if k == "_key":  # dont render
            continue
        ret += f"{tab(depth)}{bullet1}{format_task(k)}:\n" + depth_first_report(v, updates, bullet1, bullet2, depth + 1)
    return ret


def depth_first_report_flat(tree, updates, bullet):
    ret = ""
    if "_key" in tree and tree["_key"] in updates:
        key = tree["_key"]
        h = f"{bullet}{format_task(key)}: "
        ret += h + ("\n" + h).join([format_update(x) for x in updates[key]]) + "\n"
    for k, v in tree.items():
        if k == "_key":
            continue
        ret += depth_first_report_flat(v, updates, bullet)
    return ret


def write_reporttree(tasktree, updates, BULLET, BULLET2, oldformat=False):
    if oldformat:
        txt = depth_first_report_flat(tasktree, updates, BULLET)
    else:
        txt = depth_first_report(tasktree, updates, BULLET, BULLET2)
    return txt
