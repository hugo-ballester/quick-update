import pytest
from quick_update import *


@pytest.mark.parametrize(
    "line,des_task,des_update,des_done",
    [
        ("Task one:: update", "Task one", "Update.", False),
        ("Task one:: task two:: update line", task_join(("Task one", "task two")), "Update line.", False),
        (
            "Task one:: task two:: task three:: update line(.)",
            task_join(("Task one", "task two", "task three")),
            "Update line.",
            True,
        ),
        (
                "Task one:: task two:: task three:: update line  (.)",
                task_join(("Task one", "task two", "task three")),
                "Update line.",
                True,
        ),
        (
            "task1::    update CAPITALS 1_1 SIM:https://blah.com/blah?1&2 tarara",
            "task1",
            "Update CAPITALS 1_1 [SIM](https://blah.com/blah?1&2) tarara.",
            False,
        ),
        (
            "task1:: subtask11::   update CAPITALS 1_1 SIM:https://blah.com/blah?1&2 tarara",
            "task1 / subtask11",
            "Update CAPITALS 1_1 [SIM](https://blah.com/blah?1&2) tarara.",
            False,
        ),
        (
            "[alias1] task1:: subtask11::   update CAPITALS 1_1 SIM:https://blah.com/blah?1&2 tarara",
            "task1 / subtask11",
            "Update CAPITALS 1_1 [SIM](https://blah.com/blah?1&2) tarara.",
            False,
        ),
    ],
)
def test_parse_oneline_tasks(line, des_task, des_update, des_done):
    task, update, done = parse_line(line, {}, {}, {}, {})
    assert task == des_task
    assert update == des_update
    assert done == des_done




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
            "[Alias two]    Task one:: task two:: POSFIX:blah blah:",
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
            "[Alias one] Task one:: POSFIX:my posfix here:",
            {"Alias one": "Task one"},
            {},
            {"Task one": "my posfix here"},
            {},
        ),
        (
            "[Alias one] Task one:: http://test.com POSFIX:my posfix here: ORDER:z:",
            {"Alias one": "Task one"},
            {"Task one": "http://test.com"},
            {"Task one": "my posfix here"},
            {"Task one": "z"},
        ),
        (
            "[BRR] Book Research:: Reading::		POSFIX:(DONE):",
            {"BRR": "Book Research / Reading"},
            {},
            {"Book Research / Reading": "(DONE)"},
            {},
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
        ("#2001 01 01       \ntask1:: blah", "2001-01-01"),
    ],
)
def test_parse_date(file_content, des_date):
    df, _, _, _ = parse_file(file_content)
    assert 1 == df.shape[0]
    assert df.iloc[0]["Date"] == datetime.strptime(des_date, '%Y-%m-%d').date()


@pytest.mark.parametrize(
    "file_content,des_task, des_update",
    [
        ("# 2001-01-01\n[T1] task1::\nT1:: update", "task1", "Update."),
        (
            "# 2001-01-01\n[T1] task1:: POSFIX:my posfix!:\nT1:: update",
            "task1",
            "Update my posfix!",
        ),
        (
            "# 2001-01-01\n[T1] task1:: task2::\nT1:: task 3:: update",
            task_join(("task1", "task2", "task 3")),
            "Update.",
        ),
    ],
)
def test_parse_alias_replacements(file_content, des_task, des_update):
    df, _, _, _ = parse_file(file_content)
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
task1::     update 1_2 (DONE)
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
    df, _, _, _ = parse_file(lines)
    df = open_tasks(df)
    assert len(des_open_tasks) == df.shape[0]
    i = 0
    for t in des_open_tasks:
        print(t)
        print(type(t))
        assert t == df.iloc[i]["Task"]
        i += 1


def show(str):
    print("=========================")
    print("=========================")
    print(str)
    print("=========================")
    print("=========================")
