# import os, sys, time

# def clear():
#     os.system("cls" if os.name == "nt" else "clear")

# def move_cursor(y, x):
#     print(f"\033[{y};{x}H", end="")

# # Example HUD at top-right
# def hud(hp, gold):
#     move_cursor(1, 60)  # row 1, col 60
#     print(f"HP: {hp} | Gold: {gold}", end="")

# # Demo
# clear()
# print("Welcome to Dungeon Quest!")
# hud(50, 10)
# time.sleep(2)
# hud(45, 15)  # update stats in-place

import curses
import time

def main(stdscr):
    curses.curs_set(0)  # Hide cursor
    stdscr.nodelay(True)

    hp, gold = 50, 0

    for i in range(10):
        # Draw HUD at top
        stdscr.addstr(0, 0, "===================================")
        stdscr.addstr(1, 0, " ⚔️ Dungeon Quest - Stats HUD ⚔️ ")
        stdscr.addstr(2, 0, "===================================")
        stdscr.addstr(3, 0, f"HP: {hp:<3} | Gold: {gold:<3}   ")
        stdscr.addstr(4, 0, "-----------------------------------")

        # Draw game log below
        stdscr.addstr(6+i, 0, f"Turn {i+1}: Exploring the dungeon...")

        stdscr.refresh()
        time.sleep(1)

        hp -= 5
        gold += 10

    stdscr.getch()

curses.wrapper(main)
