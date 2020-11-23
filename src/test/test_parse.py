import pytest
from quick_update import *


@pytest.mark.parametrize(
    "line,des_task,des_done",
    [
        ("Task one:: update", "Task one", False),
        ("Task one:: task two:: update", task_join(("Task one", "task two")), False),
        (
            "Task one:: task two:: task three:: update (.)",
            task_join(("Task one", "task two", "task three")),
            True,
        ),
    ],
)
def test_parse_oneline_tasks(line, des_task, des_done):
    task, update, done = parse_line(line, {}, {}, {}, {})
    assert des_task == task
    assert des_done == done


@pytest.mark.parametrize(
    "line,des_update",
    [
        (
            "task1:: update 1_1 SIM:https://blah.com/blah?1&2 tarara",
            "update 1_1 [SIM](https://blah.com/blah?1&2) tarara",
        ),
    ],
)
def test_shorthands(line, des_update):
    aliases = {}
    posfix = {}
    urls = {}
    order = {}
    task, update, done = parse_line(line, {}, {}, {}, {})
    assert des_update == update


@pytest.mark.parametrize(
    "line,des_alias,des_urls,des_posfix,des_order",
    [
        ("[Alias one] Task one::", {"Alias one": "Task one"}, {}, {}, {}),
        (
            "[Alias two] Task one:: task two::",
            {"Alias two": task_join(("Task one", "task two"))},
            {},
            {},
            {},
        ),
        (
            "[Alias two] Task one:: task two:: ::POSFIX:blah blah:",
            {"Alias two": task_join(("Task one", "task two"))},
            {},
            {task_join(("Task one", "task two")): "blah blah"},
            {},
        ),
        (
            "[Alias one] Task one:: http://test.com",
            {"Alias one": "Task one"},
            {"Task one": "http://test.com"},
            {},
            {},
        ),
        (
            "[Alias one] Task one:: ::POSFIX:my posfix here:",
            {"Alias one": "Task one"},
            {},
            {"Task one": "my posfix here"},
            {},
        ),
        (
            "[Alias one] Task one:: http://test.com ::POSFIX:my posfix here: ::ORDER:z:",
            {"Alias one": "Task one"},
            {"Task one": "http://test.com"},
            {"Task one": "my posfix here"},
            {"Task one": "z"},
        ),
    ],
)
def test_parse_alias_expressions(line, des_alias, des_urls, des_posfix, des_order):
    aliases = {}
    posfix = {}
    urls = {}
    order = {}
    ret = parse_line(line, aliases, urls, posfix, order)
    assert None == ret
    assert des_alias == aliases
    assert des_posfix == posfix
    assert des_urls == urls
    assert des_order == order


@pytest.mark.parametrize(
    "file_content,des_date",
    [
        ("# 2001-01-01\ntask1:: blah", "2001-01-01"),
        ("#  2001 01 01\ntask1:: blah", "2001-01-01"),
        ("#2001 01 01\ntask1:: blah", "2001-01-01"),
    ],
)
def test_parse_date(file_content, des_date):
    df, _, _ = parse_file(file_content)
    assert 1 == df.shape[0]
    assert des_date == df.iloc[0]["Date"]


@pytest.mark.parametrize(
    "file_content,des_task, des_update",
    [
        ("# 2001-01-01\n[T1] task1::\nT1:: update", "task1", "update"),
        (
            "# 2001-01-01\n[T1] task1:: ::POSFIX:my posfix!:\nT1:: update",
            "task1",
            "update my posfix!",
        ),
        (
            "# 2001-01-01\n[T1] task1:: task2::\nT1:: task 3:: update",
            task_join(("task1", "task2", "task 3")),
            "update",
        ),
    ],
)
def test_parse_alias_replacements(file_content, des_task, des_update):
    df, _, _ = parse_file(file_content)
    assert 1 == df.shape[0]
    assert des_task == df.iloc[0]["Task"]
    assert des_update == df.iloc[0]["Update"]


@pytest.mark.parametrize(
    "lines,des_open_tasks",
    [
        (
            """# example 1
# 2020-01-01
task1:: update 1_1
task1:: update 1_2
task1:: update 1_2
""",
            ["task1"],
        ),
        (
            """# example 2
# 2020-01-01
task1:: update 1_1
task1:: update 1_2 (DONE)
""",
            [],
        ),
        (
            """# example 3
# 2020-01-01
task1:: update 1_1
task1:: update 1_2 (DONE)
task1:: update 1_2 (.)
""",
            [],
        ),
        (
            """# example 4
# 2020-01-01
task1:: update 1_1
task1:: update 1_2 (DONE)
task1:: update 1_3
""",
            ["task1"],
        ),
        (
            """# example 5
# 2010-09-01
task1:: update 1_1
task1:: update 1_2 (DONE)
task1:: task1sub1:: update 1-1_1
""",
            [task_join(("task1", "task1sub1"))],
        ),
    ],
)
def test_parse_completion(lines, des_open_tasks):
    df, _, _ = parse_file(lines)
    df = open_tasks(df, None)
    assert len(des_open_tasks) == df.shape[0]
    i = 0
    for t in des_open_tasks:
        assert t == df.iloc[i]["Task"]
        i += 1


def show(str):
    print("=========================")
    print("=========================")
    print(str)
    print("=========================")
    print("=========================")
