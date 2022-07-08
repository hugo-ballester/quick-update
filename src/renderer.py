# == RENDERER ===========================================================================================
import subprocess

import utils
from reports import BULLET


class Renderer_md():
    def __init__(self, markdown_type="slack"):
        self.buffer = ""
        self.markdown_type = markdown_type

        # Markdown flavours setup:
        supported = ["slack", "standard"]
        utils.myassert(markdown_type in supported,
                       f"Unsupported markdown_type [{markdown_type}]. Supported types: {supported}")
        self.md_BULLET = "*"
        if self.markdown_type == "slack":
            self.md_BULLET = "- "

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
        return str.replace(BULLET, self.md_BULLET)

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
        return str.replace(BULLET, "  • ")


def write_to_clipboard(string):
    process = subprocess.Popen(
        'pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
    process.communicate(string.encode('utf-8'))


def printAndCopy(string, title=None):
    r = Renderer_md()
    md = r.render(title, string, display=False)

    r = Renderer_console()
    r.render(title, string)

    write_to_clipboard(md)
