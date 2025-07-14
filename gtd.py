import curses
import sys

#19ebebf0-e438-4dba-9716-8aa11faf49d0
#af96b4c1-b058-423e-971e-a6c4f764216b
#a73e25f7-07cb-49c8-aafc-4365b2674bc4
#e24e3889-6ce4-4162-9561-b2cb6b010f27
#aae24f8b-4333-4b8b-82c2-a56593303733
#6f19c52a-e376-4e69-b8bb-84e724c41333
#607b1c35-497d-49ff-8678-96f33fe7128a
#b4b4eb29-3398-4da2-9c42-b262a984756e
#024e02b7-f0c9-4c70-86a0-5d35f3ac3d4b
#7f7a4900-2d32-4122-8917-3d15e5c5d581


def main(stdscr: curses.window):
    stdscr.clear()
    stdscr.addstr(5, 5, 'Hi.')
    stdscr.refresh()
    stdscr.getch()

curses.wrapper(main)