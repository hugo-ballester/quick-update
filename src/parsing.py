import re

TASK_SEPARATOR_INPUT = "::"  # TODO parametrise


def task_split_input(tasks):
    return re.split(f" *{TASK_SEPARATOR_INPUT} *",tasks)


def task_split_internal(tasks):
    return tasks.split(f"{TASK_SEPARATOR_INPUT}")


def task_join_internal(tasks):
    return TASK_SEPARATOR_INPUT.join(tasks)


def task_split_external(tasks):
    return tasks.split(" / ")


def task_join_external(tasks):
    return " / ".join(tasks)