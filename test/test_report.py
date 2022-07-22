import pytest

from quick_update import parse_file
from reports import report, report_old

bold = "\x1b[1m"
endbold = "\x1b[0m"


def test_report_old():
    file_content = """
#2022-07-21
Title A:: title AA:: update text here
Title A:: title AB:: update text here
Title A:: title AB:: third title A:: update text here
Title B:: update text here
"""
    df, _, _, _, _ = parse_file(file_content)
    rep = report(df, oldformat=True)
    assert rep == """\
  _*_ Title A::title AA: Update text here.
  _*_ Title A::title AB: Update text here.
  _*_ Title A::title AB::third title A: Update text here.
  _*_ Title B: Update text here.
""".replace("Title",bold+"Title").replace(": U",endbold+": U")


def test_report():
    file_content = """
#2022-07-21
Title A:: Title AA:: update text here 1
Title A:: Title AB:: update text here 2
Title A:: Title AB:: Title ABA:: update text here 3
Title B:: update text here 4
"""
    df, _, _, _, _ = parse_file(file_content)
    rep = report(df)
    des = """\
  _*_ Title A:
    _*_ Title AA:
      _o_ Update text here 1.
    _*_ Title AB:
      _o_ Update text here 2.
      _*_ Title ABA:
        _o_ Update text here 3.
  _*_ Title B:
    _o_ Update text here 4.
""".replace("Title",bold+"Title").replace(":",endbold+":")
    for (a, d) in zip(rep.split("\n"), des.split("\n")):
        assert a == d

