import pytest

from src.renderer import Renderer_md
from src.reports import BULLET

bullet1 = Renderer_md(markdown_type="standard").md_BULLET
bullet2 = Renderer_md(markdown_type="slack").md_BULLET


@pytest.mark.parametrize(
    "title, txt, des_md, des_md_slack",
    [
        (None, "text", "text\n", None),
        ("TITLE", "text", "**TITLE**\ntext\n", "*TITLE*\ntext\n"),
        ("TITLE", BULLET + "text", f"**TITLE**\n{bullet1}text\n", f"*TITLE*\n{bullet2}text\n"),
    ],
)
def test_render(title, txt, des_md, des_md_slack):
    des_md_slack = des_md if des_md_slack is None else des_md_slack
    r = Renderer_md(markdown_type="standard")
    res = r.render(title, txt, display=False)
    assert res == des_md

    r = Renderer_md(markdown_type="slack")
    res = r.render(title, txt, display=False)
    assert res == des_md_slack
