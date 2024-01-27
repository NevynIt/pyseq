import curses
import curses.panel

def main(stdscr):
    # Setup the main window
    curses.curs_set(0)
    stdscr.clear()
    stdscr.box()
    stdscr.addstr(1, 1, "Main window (Press 'p' to show/hide panel, 'q' to quit)")

    # Create a new window and put it in a panel
    panel_win = curses.newwin(10, 20, 5, 5)
    panel_win.box()
    panel_win.addstr(1, 1, "Panel Window")
    panel = curses.panel.new_panel(panel_win)

    # Hide the panel initially
    panel.hide()
    curses.panel.update_panels()
    stdscr.refresh()

    while True:
        ch = stdscr.getch()
        
        if ch == ord('q'):
            break
        elif ch == ord('p'):
            # if panel.hidden():
            #     panel.show()
            # else:
            #     panel.hide()
            panel.show()
            curses.panel.update_panels()
            stdscr.refresh()

# Initialize curses
curses.wrapper(main)
