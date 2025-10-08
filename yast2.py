import curses
import time
import sys
import json
import argparse
import os
import random
import subprocess
from datetime import date, datetime, timedelta

BAR_WIDTH_PERCENT = 0.50
DEFAULT_DURATION_MIN = 15
DEFAULT_PEOPLE_FILE = "people.txt"
LOG_FILE = "standup_log.json"

DAYS = [
    (date.today() - timedelta(days=i)).isoformat() for i in range(6, -1, -1)
]

def format_time(seconds):
    seconds = int(round(seconds))
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"

def log_time(name, duration):
    log_entry = {
        "date": date.today().isoformat(),
        "name": name,
        "duration_seconds": round(duration)
    }
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append(log_entry)

    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_detailed_weekly_report():
    if not os.path.exists(LOG_FILE):
        return {}
    with open(LOG_FILE, "r") as f:
        data = json.load(f)

    week_data = [entry for entry in data if entry['date'] in DAYS]

    report = {name: {d: 0 for d in DAYS} for name in set(e['name'] for e in week_data)}
    for entry in week_data:
        report[entry['name']][entry['date']] += entry['duration_seconds']
    return report

def export_termgraph_csv(report):
    filename = "standup_termgraph_data.csv"
    days_short = [d[5:] for d in DAYS]
    with open(filename, "w") as f:
        f.write("""Name,""" + ",".join(days_short) + """
""")
        for name, daydata in sorted(report.items()):
            values = [str(round(daydata[d] / 60)) for d in DAYS]
            f.write("""{}""".format(name + "," + ",".join(values)) + """
""")
    return filename

def run_weekly_report(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.erase()

    report = get_detailed_weekly_report()
    stdscr.addstr(0, 2, "Weekly Standup Report", curses.A_BOLD | curses.A_UNDERLINE)
    if not report:
        stdscr.addstr(2, 2, "No data found for the past 7 days.")
    else:
        max_name_len = max(len(name) for name in report)
        for i, (name, daydata) in enumerate(sorted(report.items())):
            line = f"{name:<{max_name_len}} : "
            for d in DAYS:
                mins = round(daydata[d] / 60)
                bar = "#" * (mins if mins > 0 else 0)
                line += f"{bar:<10}"
            stdscr.addstr(2 + i, 2, line)

        header = "".ljust(max_name_len + 3) + " ".join([d[5:] for d in DAYS])
        stdscr.addstr(1, 2, header, curses.A_BOLD)

        stdscr.addstr(len(report) + 4, 2, "Press any key to view termgraph chart...", curses.A_BOLD)
        stdscr.refresh()
        stdscr.getch()

        curses.endwin()
        csv_file = export_termgraph_csv(report)
        print("""
Launching termgraph chart:
""")
        try:
            subprocess.run(["termgraph", csv_file, "--stacked"])
        except FileNotFoundError:
            print("termgraph is not installed. Please install it with: pip install termgraph")

def run_meeting(stdscr, total_meeting_secs, participant_secs, people):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)

    curses.start_color()
    curses.use_default_colors()
    curses.init_color(curses.COLOR_GREEN, 0, 1000, 0)
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_YELLOW, -1)
    curses.init_pair(3, curses.COLOR_RED, -1)

    meeting_start = time.time()
    participant_starts = [0] * len(people)
    participant_times = [participant_secs] * len(people)
    participant_share = [participant_secs] * len(people)
    finished_states = [None] * len(people)
    current_participant = 0
    total_participants = len(people)

    height, width = stdscr.getmaxyx()
    max_participants = height - 8

    participant_starts[current_participant] = meeting_start

    while current_participant < total_participants:
        now = time.time()
        total_elapsed = now - meeting_start
        height, width = stdscr.getmaxyx()
        bar_length = int(width * BAR_WIDTH_PERCENT)

        stdscr.erase()
        stdscr.addstr(0, 2, f"Total Participants: {total_participants}", curses.A_BOLD)

        for idx in range(total_participants):
            name = people[idx]
            if idx < current_participant:
                state = finished_states[idx]
                if state:
                    disp_time, bar, color = state['disp_time'], state['bar'], state['color']
                else:
                    disp_time = format_time(participant_share[idx])
                    bar = "=" * bar_length
                    color = curses.color_pair(1)
            elif idx == current_participant:
                elapsed = now - participant_starts[idx]
                remaining = participant_share[idx] - elapsed
                participant_times[idx] = remaining

                if remaining >= 0:
                    disp_time = format_time(remaining)
                    ratio = remaining / participant_share[idx]
                    color = curses.color_pair(2) if ratio <= 0.25 else curses.color_pair(1)
                    equals = int(round(ratio * bar_length))
                    dashes = bar_length - equals
                    bar = "=" * equals + "-" * dashes
                else:
                    overtime = abs(remaining)
                    disp_time = format_time(overtime)
                    color = curses.color_pair(3)
                    ratio = min(overtime / participant_share[idx], 1.0)
                    equals = int(round(ratio * bar_length))
                    dashes = bar_length - equals
                    bar = "-" * dashes + "✝" * equals
            else:
                remaining = participant_share[idx]
                disp_time = format_time(remaining)
                bar = "-" * bar_length
                color = curses.color_pair(1)

            line = f"#{idx+1:>2d} {name:<12s} {disp_time}  [ {bar} ]"
            stdscr.addstr(2 + idx, 2, line, color)

        total_line = f"Planned: {format_time(total_meeting_secs)}   Elapsed: {format_time(total_elapsed)}"
        color_total = curses.color_pair(3) if total_elapsed > total_meeting_secs else curses.color_pair(1)
        stdscr.addstr(4 + total_participants, 2, total_line, color_total)
        stdscr.addstr(6 + total_participants, 2, "Press SPACE to switch, A to add a participant.", curses.A_BOLD)
        stdscr.refresh()

        key = stdscr.getch()
        if key == ord(' '):
            elapsed = now - participant_starts[current_participant]
            log_time(people[current_participant], elapsed)
            current_participant += 1
            if current_participant < total_participants:
                participant_starts[current_participant] = now

        elif key in (ord('a'), ord('A')):
            if total_participants < max_participants:
                total_participants += 1
                name = f"User{total_participants}"
                people.append(name)
                participant_starts.append(now)
                participant_times.append(participant_secs)
                participant_share.append(participant_secs)
                finished_states.append(None)
                remaining_meeting = max(total_meeting_secs - total_elapsed, 0)
                num_slots = total_participants - current_participant
                new_alloc = remaining_meeting / num_slots if num_slots > 0 else 0
                for i in range(current_participant, total_participants):
                    participant_times[i] = new_alloc
                    participant_share[i] = new_alloc

        time.sleep(0.1)

    stdscr.addstr(1, 2, "Meeting complete. Press x to exit.", curses.A_BOLD)
    stdscr.refresh()
    stdscr.nodelay(False)
    while True:
        key = stdscr.getch()
        if key in (ord('x'), ord('X')):
            break

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default=DEFAULT_PEOPLE_FILE, help="Path to people file")
    parser.add_argument("--time", type=int, default=DEFAULT_DURATION_MIN, help="Total duration in minutes")
    parser.add_argument("--report", action="store_true", help="Show weekly report")
    args = parser.parse_args()

    if args.report:
        curses.wrapper(run_weekly_report)
        return

    if not os.path.exists(args.file):
        print(f"File not found: {args.file}")
        return

    with open(args.file) as f:
        people = [line.strip() for line in f if line.strip()]

    random.shuffle(people)

    total_meeting_seconds = args.time * 60
    participant_seconds = total_meeting_seconds / len(people)

    curses.wrapper(run_meeting, total_meeting_seconds, participant_seconds, people)

if __name__ == "__main__":
    main()
