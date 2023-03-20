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
            if linp.startswith("sum"):
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
                self.text = self.db.backend.command(inp.split())[0].split("\n")
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
            if self.hpos >= self.maxtlen - 2:
                curses.beep()
                curses.flash()
            else:
                self.hpos += 1
        elif keypress == "KEY_LEFT":
            if self.hpos <= 0:
                curses.beep()
                curses.flash()
            else:
                self.hpos -= 1
        return inputResponses.NORMAL

    def draw(self):
        self.win.clear()
        self.win.insstr(
            0,
            0,
            "\n".join([x[self.hpos :] for x in self.text[self.vpos :]]),
            self.cpairs.BODY,
        )
