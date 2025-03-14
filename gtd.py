import curses

def main(stdscr: curses.window):
    stdscr.clear()
    stdscr.addstr(5, 5, 'Hi.')
    stdscr.refresh()
    stdscr.getch()

curses.wrapper(main)