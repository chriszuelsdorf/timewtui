from basetui_ncurses import SubProgTemplate
from basetui_ncurses.enums import inputResponses
import curses
import time
import traceback
from .backend import twBackend
from .custom_reports import SumN


class GenericObject:
    pass


class timewTUI(SubProgTemplate):
    def __init__(self) -> None:
        super().__init__()
        self.db = GenericObject()
        self.text = ["No output yet."]
        self.maxtlen = max([len(x) for x in self.text])
        self.hpos = 0
        self.vpos = 0
        self.config = GenericObject()
        self.config.hscroll = 1

    def updatedb(self):
        if not hasattr(self.db, "backend"):
            self.db.backend = twBackend(logger=self.log)
        self.db.data = self.db.backend.command(["export"])[0]
        self.db.last_update = time.time()

    def handleInput(self, inp):
        linp = inp.lower()
        self.updatedb()
        self.log(self.db.data, 8)
        try:
            if linp.startswith("set "):
                sw = linp.split(" ")
                if sw[1] == "hscroll":
                    if len(sw) == 3 and sw[2].isnumeric():
                        self.config.hscroll = int(sw[2])
                        self.text = [f"Set hscroll to {sw[2]}"]
                    else:
                        self.text = [
                            "Invalid value provided for hscroll. Must be a "
                            "numeric argument."
                        ]
                else:
                    self.text = [f"Unrecognized set command `{sw[1]}`."]
            elif linp.startswith("sum"):
                if linp[3:].isnumeric() or len(linp) == 3:
                    self.text = SumN(self.db.data).getout(
                        1 if len(linp) == 3 else int(linp[3:]), self.log
                    )
                else:
                    self.text = (
                        "SUMn report requires either a numeric specifier or, "
                        "for 1 day, no further specification."
                    )
            elif linp.startswith("det"):
                self.text = self.db.backend.command(
                    f"timew summary :id{inp[3:]}".split()
                )[0].split("\n")
            else:
                response = self.db.backend.command(inp.split())
                self.text = response[1 if len(response[1]) != 0 else 0].split(
                    "\n"
                )
        except Exception as e:
            self.log(f"ERROR:\n{type(e)}\n{e}\n{traceback.format_exc()}", 1)
            self.text = ["Encountered an error. Please try again.", str(e)]
        self.hpos = 0
        self.vpos = 0
        self.maxtlen = max([len(x) for x in self.text])
        return inputResponses.NORMAL

    def handleKeypress(self, keypress):
        if keypress == "KEY_UP":
            if self.vpos <= 0:
                curses.beep()
                curses.flash()
            else:
                self.vpos -= 1
        elif keypress == "KEY_DOWN":
            if self.vpos >= len(self.text) - 1:
                curses.beep()
                curses.flash()
            else:
                self.vpos += 1
        elif keypress == "KEY_RIGHT":
            if self.hpos >= self.maxtlen - 1:
                curses.beep()
                curses.flash()
            else:
                self.hpos += min(
                    self.maxtlen - self.hpos - 1, self.config.hscroll
                )
        elif keypress == "KEY_LEFT":
            if self.hpos <= 0:
                curses.beep()
                curses.flash()
            else:
                self.hpos -= min(self.hpos, self.config.hscroll)
        return inputResponses.NORMAL

    def draw(self):
        self.win.clear()
        lines, cols = self.win.getmaxyx()
        for ln in range(min(lines, len(self.text) - self.vpos)):
            self.win.insstr(
                ln, 0, self.text[ln + self.vpos][self.hpos :], self.cpairs.BODY
            )
        # self.win.insstr(
        #     0,
        #     0,
        #     "\n".join([x[self.hpos :] for x in self.text[self.vpos :]]),
        #     self.cpairs.BODY,
        # )
