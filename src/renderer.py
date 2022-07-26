# == RENDERER ===========================================================================================
import re
import subprocess

import utils
from reports import BULLET, BULLET2

BULLET_MARKDOWN = "* "
BULLET_MARKDOWN_SLACK = "- "


class Renderer_md():
    def __init__(self, markdown_type="slack"):
        self.buffer = ""
        self.markdown_type = markdown_type

        # Markdown flavours setup:
        supported = ["slack", "standard"]
        utils.myassert(markdown_type in supported,
                       f"Unsupported markdown_type [{markdown_type}]. Supported types: {supported}")
        self.md_BULLET = BULLET_MARKDOWN_SLACK if self.markdown_type == "slack" else BULLET_MARKDOWN

    def boldit(self, str):
        if self.markdown_type == "slack":
            return "*" + str + "*"
        else:
            return "**" + str + "**"

    def title(self, str):
        self.buffer += self.boldit(str) + "\n"

    def start(self):
        pass

    def end(self):
        pass

    def replace_bullet(self, str):
        # HACK, render lists instead
        return str.replace(BULLET, self.md_BULLET).replace(BULLET2, self.md_BULLET)

    def format_task(update):
        return update.title()

    def format_update(update):
        if not re.match("[.!?]", update[-1]):
            update += "."

        update = f"{update[0].upper()}{update[1:]}"
        return update

    def txt(self, str):
        str = self.replace_bullet(str)
        self.buffer += str + "\n"

    def flush(self, display=True):
        ret = self.buffer
        self.buffer = ""
        if display:
            print(ret)
        return ret

    def render(self, title, body, display=True):
        self.start()
        if title:
            self.title(title)
        self.txt(body)
        self.end()
        txt = self.flush(display)
        return txt


class Renderer_console(Renderer_md):
    bold_str = "\033[1m"
    end_str = "\033[0m"
    terminal_cols = 20
    headline1 = None

    def __init__(self):
        super().__init__()
        terminal_cols = 80
        try:
            _, terminal_cols = subprocess.check_output(["stty", "size"]).decode().split()
        except:
            pass
        headline1 = "_" * int(terminal_cols)
        Renderer_console.headline1 = self.boldit(headline1)

    def boldit(self, str):
        return f"{Renderer_console.bold_str}{str}{Renderer_console.end_str}"

    def start(self):
        self.buffer += "\n" + Renderer_console.headline1 + "\n\n"

    def end(self):
        self.buffer += Renderer_console.headline1 + "\n"

    def replace_bullet(self, str):
        # HACK, render lists instead
        return str.replace(BULLET, "  • ").replace(BULLET2, "  ◦ ")


class Renderer_console_plain(Renderer_md):

    # This is a hack to remove console bold to cut and paste text
    def txt(self, str):
        str = str.replace(Renderer_console.bold_str, "")
        str = str.replace(Renderer_console.end_str, "")
        super().txt(str)


def write_to_clipboard(string):
    process = subprocess.Popen(
        'pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
    process.communicate(string.encode('utf-8'))


def printAndCopy(string, title=None):
    # r = Renderer_md()
    # md = r.render(title, string, display=False)

    r = Renderer_console()
    r.render(title, string)

    r2 = Renderer_console_plain()
    txt = r2.render(title, string, display=False)
    write_to_clipboard(txt)


def printAndCopy_tree(tree, updates, title=None):
    r = Renderer_console()
    txt = r.render_reporttree(tree, updates)
    r.render(title, txt)

    r2 = Renderer_console_plain()
    txt = r.render_reporttree(tree, updates)
    txt = r2.render(title, txt, display=False)
    write_to_clipboard(txt)
