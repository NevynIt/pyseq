import curses

def main(stdscr):
    while True:
        ch = stdscr.getch()
        stdscr.addstr(0, 0, f"Event {ch}")
        stdscr.refresh()
        if ch == 'q':
            break

# Initialize curses
curses.wrapper(main)