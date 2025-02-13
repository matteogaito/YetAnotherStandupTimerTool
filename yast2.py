import curses
import time

BAR_WIDTH_PERCENT = 0.66

def format_time(seconds):
    """Format seconds into MM:SS string."""
    seconds = int(round(seconds))
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"

def run_meeting(stdscr, total_meeting_secs, participant_secs, num_participants):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)

    # Initialize color pairs: green, yellow, red
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_YELLOW, -1)
    curses.init_pair(3, curses.COLOR_RED, -1)

    meeting_start = time.time()
    participant_starts = [0] * num_participants
    participant_times = [participant_secs] * num_participants
    finished_states = [None] * num_participants
    current_participant = 0

    # Start the first participant immediately
    participant_starts[current_participant] = meeting_start

    while current_participant < num_participants:
        now = time.time()
        total_elapsed = now - meeting_start
        height, width = stdscr.getmaxyx()
        bar_length = int(width * BAR_WIDTH_PERCENT)

        stdscr.erase()

        for idx in range(num_participants):
            participant_num = idx + 1  # Display number
            if idx < current_participant:
                # Display finished state snapshot
                state = finished_states[idx]
                disp_time, bar, color = state['disp_time'], state['bar'], state['color']
            elif idx == current_participant:
                # Current participant
                elapsed = now - participant_starts[idx]
                remaining = participant_secs - elapsed
                participant_times[idx] = remaining

                # Decide current mode: countdown or overtime
                if remaining >= 0:
                    # Countdown mode
                    disp_time = format_time(remaining)
                    ratio = remaining / participant_secs
                    # Color: green normally, yellow if <= 25% time remains (i.e. >75% elapsed)
                    if ratio <= 0.25:
                        color = curses.color_pair(2)
                    else:
                        color = curses.color_pair(1)
                    # Progress bar: number of '=' equals = floor(ratio * bar_length)
                    equals = int(round(ratio * bar_length))
                    dashes = bar_length - equals
                    bar = "=" * equals + "-" * dashes
                else:
                    # Overtime mode: timer counts up overtime
                    overtime = abs(remaining)
                    disp_time = format_time(overtime)
                    color = curses.color_pair(3)
                    # In overtime, progress bar fills from left to right.
                    # Ratio relative to allocated participant_secs (clamped to 1.0)
                    ratio = min(overtime / participant_secs, 1.0)
                    equals = int(round(ratio * bar_length))
                    dashes = bar_length - equals
                    bar = "-" * dashes + "✝" * equals  # fill from right side with skull emojis
            else:
                # Future participants
                remaining = participant_secs
                disp_time = format_time(remaining)
                bar = "-" * bar_length
                color = curses.color_pair(1)

            # Build participant line string
            participant_line = f"Participant #{participant_num:>2d}  {disp_time}  [ {bar} ]"
            stdscr.addstr(2 + participant_num, 2, participant_line, color)

        total_line = f"Planned: {format_time(total_meeting_secs)}   Elapsed: {format_time(total_elapsed)}"
        color_total = curses.color_pair(3) if total_elapsed > total_meeting_secs else curses.color_pair(1)
        stdscr.addstr(4 + num_participants, 2, total_line, color_total)


        stdscr.addstr(6 + num_participants, 2, "Press SPACE to switch to next participant.", curses.A_BOLD)
        stdscr.refresh()

        # Check for spacebar to move to next participant
        key = stdscr.getch()
        if key == ord(' '):
            # Freeze the current participant's state in finished_states
            if current_participant < num_participants:
                # Compute final snapshot for current participant
                elapsed = now - participant_starts[current_participant]
                remaining = participant_secs - elapsed
                if remaining >= 0:
                    disp_time = format_time(remaining)
                    ratio = remaining / participant_secs
                    color = curses.color_pair(2) if ratio <= 0.25 else curses.color_pair(1)
                    equals = int(round(ratio * bar_length))
                    dashes = bar_length - equals
                    bar = "=" * equals + "-" * dashes
                else:
                    overtime = abs(remaining)
                    disp_time = format_time(overtime)
                    color = curses.color_pair(3)
                    ratio = min(overtime / participant_secs, 1.0)
                    equals = int(round(ratio * bar_length))
                    dashes = bar_length - equals
                    bar = "-" * dashes + "✝" * equals
                finished_states[current_participant] = {
                    'disp_time': disp_time,
                    'bar': bar,
                    'color': color
                }
                current_participant += 1
                if current_participant < num_participants:
                    participant_starts[current_participant] = now

        time.sleep(0.1)

    # End meeting screen message
    stdscr.addstr(8 + num_participants , 2, "Meeting complete. Press x to exit.", curses.A_BOLD)
    stdscr.refresh()
    stdscr.nodelay(False)
    while True:
        key = stdscr.getch()
        if key in (ord('x'), ord('X')):
            break

def main():
    try:
        total_time = float(input("Enter total meeting time (in minutes): "))
    except ValueError:
        print("Invalid input, please enter a number.")
        return

    try:
        participants = int(input("Enter number of participants: "))
    except ValueError:
        print("Invalid input, please enter an integer.")
        return

    while True:
        ready = input("Ready to start meeting? (yes/no): ").strip().lower()
        if ready in ["yes", "y"]:
            break
        elif ready in ["no", "n"]:
            print("Meeting aborted.")
            return
        else:
            print("Invalid input, please enter 'yes' or 'no'.")

    total_meeting_seconds = total_time * 60
    participant_seconds = total_meeting_seconds / participants

    curses.wrapper(run_meeting, total_meeting_seconds, participant_seconds, participants)

if __name__ == "__main__":
    main()