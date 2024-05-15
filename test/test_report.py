from src import reports, reporttree
from src.parsing import parse_file

bold = "\x1b[1m"
endbold = "\x1b[0m"


def test_write_reporttree_old():
    file_content = """
#2022-07-21
TITLE A:: title AA:: update text here 1
TITLE A:: title AB:: update text here 2.
TITLE A:: title AB:: title ABA:: update text here 3!
TITLE B:: update text here
"""
    df, _, _, _, _ = parse_file(file_content)
    title, tree, updates = reports.report_span(df, None, None)
    # TODO: test tress here

    rep = reporttree.write_reporttree(tree, updates, reports.BULLET, reports.BULLET2, oldformat=True)
    des = """\
  _*_ TITLE A::Title AA: Update text here 1.
  _*_ TITLE A::Title AB: Update text here 2.
  _*_ TITLE A::Title AB::Title ABA: Update text here 3!
  _*_ TITLE B: Update text here.
""".replace("TITLE", bold + "TITLE").replace(": U", endbold + ": U")  # full task linke in bold
    for (a, d) in zip(rep.split("\n"), des.split("\n")):
        assert a == d


def test_write_reporttree():
    file_content = """
#2022-07-21
Title A:: title AA:: update text here 1
Title A:: title AB:: update text here 2.
Title A:: title AB:: title ABA:: update text here 3!
Title B:: update text here 4
"""
    df, _, _, _, _ = parse_file(file_content)
    title, tree, updates = reports.report_span(df, None, None)
    # TODO: test tress here

    rep = reporttree.write_reporttree(tree, updates, reports.BULLET, reports.BULLET2, oldformat=False)
    des = """\
  _*_ Title A:
    _*_ Title AA:
      _o_ Update text here 1.
    _*_ Title AB:
      _o_ Update text here 2.
      _*_ Title ABA:
        _o_ Update text here 3!
  _*_ Title B:
    _o_ Update text here 4.
""".replace("T", bold + "T").replace(":", endbold + ":")  # each individual task linke in bold
    for (a, d) in zip(rep.split("\n"), des.split("\n")):
        assert a == d
