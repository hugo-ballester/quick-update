import pytest

from src.parsing import parse_file

@pytest.mark.parametrize(
    "file_content, des_task_order",
    [
        (
            "# 2001-01-01\n[T1] Task1::\nT1:: update t1\nBBBB:: update aaa",
            ["BBBB", "Task1"],
        ),
        (
            "# 2001-01-01\n[T1] Task1:: ORDER<0>\nT1:: update t1\nBBBB:: update aaa",
            ["Task1", "BBBB"],
        ),
        (
            "# 2001-01-01\n[T1] Task1:: ORDER<z>\nT1:: update t1\nWhat:: update aaa",
            ["What", "Task1"],
        ),
    ],
)
def test_order(file_content, des_task_order):
    df, todos, posfixes, date_ascending, aliases = parse_file(file_content)
    df = df.sort_values("Order")
    tasks = df.Task.tolist()
    assert tasks == des_task_order
