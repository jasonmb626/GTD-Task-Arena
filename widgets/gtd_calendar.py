import curses

class GTDCalendarData:
    def __init__(self, sched: list):
        self.sched = sched

class DrawGTDCalendar:
    @staticmethod
    def init_colors():
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_WHITE)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_WHITE)
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_WHITE)
        curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_YELLOW)
        curses.init_pair(6, curses.COLOR_GREEN, curses.COLOR_RED)
        curses.init_pair(7, curses.COLOR_RED, curses.COLOR_BLUE)
        curses.init_pair(8, curses.COLOR_BLUE, curses.COLOR_GREEN)
        curses.init_pair(9, curses.COLOR_GREEN, curses.COLOR_MAGENTA)
        curses.init_pair(10, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(11, curses.COLOR_CYAN, curses.COLOR_MAGENTA)
        curses.init_pair(12, curses.COLOR_RED, curses.COLOR_YELLOW)
        curses.init_pair(13, curses.COLOR_MAGENTA, curses.COLOR_YELLOW)
        curses.init_pair(14, curses.COLOR_CYAN, curses.COLOR_BLUE)
        curses.init_pair(15, curses.COLOR_GREEN, curses.COLOR_WHITE)
