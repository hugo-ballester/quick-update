from datetime import datetime
import pytest

from reports import *


@pytest.mark.parametrize(
    "line,des_task,des_update,des_done",
    [
        ("Task one:: update", "Task one", "update", None),
        ("Task one:: task two:: update line", task_join_internal(("Task one", "task two")), "update line", None),
        (
                "Task one:: task two:: task three:: update line(.)",
                task_join_internal(("Task one", "task two", "task three")),
                "update line",
                "DONE",
        ),
        (
                "Task one:: task two:: task three:: update line  (.)",
                task_join_internal(("Task one", "task two", "task three")),
                "update line",
                "DONE",
        ),
        (
                "task1::    update CAPITALS 1_1 SIM:https://blah.com/blah?1&2 tarara",
                "task1",
                "update CAPITALS 1_1 [SIM](https://blah.com/blah?1&2) tarara",
                None,
        ),
        (
                "task1:: subtask11::   update CAPITALS 1_1 SIM:https://blah.com/blah?1&2 tarara",
                task_join_internal(["task1", "subtask11"]),
                "update CAPITALS 1_1 [SIM](https://blah.com/blah?1&2) tarara",
                None,
        ),
        (
                "[alias1] task1:: subtask11::   update CAPITALS 1_1 SIM:https://blah.com/blah?1&2 tarara",
                "alias1",
                "update CAPITALS 1_1 [SIM](https://blah.com/blah?1&2) tarara",
                None,
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
                {"Alias two": task_join_internal(("Task one", "task two"))},
                {},
                {},
                {},
        ),
        (
                "[Alias two]   Task one:: task two:: POSTFIX<blah blah>",
                {"Alias two": task_join_internal(("Task one", "task two"))},
                {},
                {task_join_internal(("Task one", "task two")): "blah blah"},
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
                "[Alias one] Task one:: POSTFIX<my postfixes here>",
                {"Alias one": "Task one"},
                {},
                {"Task one": "my postfixes here"},
                {},
        ),
        (
                "[Alias one] Task one:: http://test.com POSTFIX<my postfixes here> ORDER<z>",
                {"Alias one": "Task one"},
                {"Task one": "http://test.com"},
                {"Task one": "my postfixes here"},
                {"Task one": "z"},
        ),
        (
                "[BRR] Book Research:: Reading::		POSTFIX<(.)>",
                {"BRR": task_join_internal(["Book Research", "Reading"])},
                {},
                {task_join_internal(["Book Research", "Reading"]): "(.)"},
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
    assert ret == None
    assert aliases == des_alias
    assert posfix == des_posfix
    assert urls == des_urls
    assert order == des_order


@pytest.mark.parametrize(
    "file_content,des_date",
    [
        ("# 2001-01-01\ntask1:: blah", "2001-01-01"),
        ("#  2001 01 01\ntask1:: blah", "2001-01-01"),
        ("#2001 01 01       \ntask1:: blah", "2001-01-01"),
    ],
)
def test_parse_date(file_content, des_date):
    df, _, _, _, _ = parse_file(file_content)
    assert 1 == df.shape[0]
    assert df.iloc[0]["Date"] == datetime.strptime(des_date, '%Y-%m-%d').date()


@pytest.mark.parametrize(
    "file_content,des_task, des_update, des_done",
    [
        # Basic:
        ("# 2001-01-01\n[T1] task1::\nT1:: update", "task1", "update", None),
        # Basic with DONE:
        ("# 2001-01-01\n[T1] task1:: POSTFIX<(.)>\nT1:: update", "task1", "update", "DONE"),
        (
                "# 2001-01-01\n[T1] task1:: POSTFIX<my postfixes!>\nT1:: update",
                "task1",
                "update my postfixes!", None
        ),
        # update with extended task:
        (
                "# 2001-01-01\n[T1] task1:: task2::\nT1:: task 3:: update",
                task_join_internal(("task1", "task2", "task 3")),
                "update", None
        ),
        # update with extended task, alias comes later:
        (
                "# 2001-01-01\nT1:: task 3:: update\n[T1] task1:: task2::",
                task_join_internal(("task1", "task2", "task 3")),
                "update", None
        ),
        # update with pending:
        ("# 2001-01-01\ntask1:: update last (!)", "task1", "update last (!)", "PENDING")
    ],
)
def test_parse_alias_replacements(file_content, des_task, des_update, des_done):
    df, _, _, _, _ = parse_file(file_content)
    assert 1 == df.shape[0]
    assert df.iloc[0]["Task"] == des_task
    assert df.iloc[0]["Update"] == des_update
    assert df.iloc[0]["Done"] == des_done


@pytest.mark.parametrize(
    "lines,des_open_tasks,des_standby_tasks,des_pending_tasks",
    [
        (
                """# example 1
# 2020-01-01
task1:: update 1_1
task1:: update 1_2
task1:: update 1_2
""",
                ["task1"], [], [],
        ),
        (
                """# example 2
# 2020-01-01
task1:: update 1_1
task1::     update 1_2 (.)
""",
                [], [], [],
        ),
        (
                """# example 3
# 2020-01-01
task1:: update 1_1
task1:: update 1_2 (.)
""",
                [], [], [],
        ),
        (
                """# example 4
# 2020-01-01
task1:: update 1_1
task1:: update 1_3
task2:: update 1_2 (,)
""",
                ["task1"], ["task2"], [],
        ),
        (
                """# example 5
# 2010-09-01
task1:: update 1_1
task1:: update 1_2 (.)
task1:: task1sub1:: update 1-1_1
""",
                [task_join_internal(("task1", "task1sub1"))], [], [],
        ),
        (
                """# example 5 (pending)
# 2010-09-01
task1:: update 1_1 (.)
task1:: update 1_2 (!)
task1:: task1sub1:: update 1-1_1
""",
                [task_join_internal(("task1", "task1sub1"))], [], ["task1"]
        ),
    ],
)
def test_parse_completion(lines, des_open_tasks, des_standby_tasks, des_pending_tasks):
    def check(df, des):
        assert len(des) == df.shape[0]
        i = 0
        for t in des:
            assert t == df.iloc[i]["Task"]
            i += 1

    df, _, _, _, _ = parse_file(lines)
    df2 = completion_tasks(df, None)  # open
    print(df[["Task","Done"]])
    print(df2[["Task","Done"]])
    check(df2, des_open_tasks)
    df2 = completion_tasks(df, "STANDBY")  # open
    check(df2, des_standby_tasks)
    df2 = completion_tasks(df, "PENDING")  # open
    check(df2, des_pending_tasks)


def show(str):
    print("=========================")
    print("=========================")
    print(str)
    print("=========================")
    print("=========================")
