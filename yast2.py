import curses
import time
import sys

BAR_WIDTH_PERCENT = 0.50

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
    curses.init_color(curses.COLOR_GREEN, 0, 1000, 0)  # Set green color explicitly
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_YELLOW, -1)
    curses.init_pair(3, curses.COLOR_RED, -1)

    meeting_start = time.time()
    participant_starts = [0] * num_participants
    participant_times = [participant_secs] * num_participants
    participant_share = [participant_secs] * num_participants
    finished_states = [None] * num_participants
    current_participant = 0
    total_participants = num_participants 

    # Calculate max participants based on available screen lines
    height, width = stdscr.getmaxyx()
    max_participants = height - 8  # 10 lines reserved for other messages

    # Start the first participant immediately
    participant_starts[current_participant] = meeting_start

    while current_participant < total_participants:
        now = time.time()
        total_elapsed = now - meeting_start
        height, width = stdscr.getmaxyx()
        bar_length = int(width * BAR_WIDTH_PERCENT)

        stdscr.erase()

        stdscr.addstr(0, 2, f"Total Participants: {total_participants}", curses.A_BOLD)

        for idx in range(total_participants):
            participant_num = idx + 1  # Display number
            if idx < current_participant:
                # Display finished state snapshot
                state = finished_states[idx]
                disp_time, bar, color = state['disp_time'], state['bar'], state['color']
            elif idx == current_participant:
                # Current participant
                elapsed = now - participant_starts[idx]
                remaining = participant_share[idx] - elapsed
                participant_times[idx] = remaining

                # Decide current mode: countdown or overtime
                if remaining >= 0:
                    # Countdown mode
                    disp_time = format_time(remaining)
                    ratio = remaining / participant_share[idx]
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
                    ratio = min(overtime / participant_share[idx], 1.0)
                    equals = int(round(ratio * bar_length))
                    dashes = bar_length - equals
                    bar = "-" * dashes + "✝" * equals  # fill from right side with skull emojis
            else:
                # Future participants
                remaining = participant_share[idx]
                disp_time = format_time(remaining)
                bar = "-" * bar_length
                color = curses.color_pair(1)

            # Build participant line string
            participant_line = f"#{participant_num:>2d}  {disp_time}  [ {bar} ]"
            stdscr.addstr(2 + participant_num, 2, participant_line, color)

        total_line = f"Planned: {format_time(total_meeting_secs)}   Elapsed: {format_time(total_elapsed)}"
        color_total = curses.color_pair(3) if total_elapsed > total_meeting_secs else curses.color_pair(1)
        stdscr.addstr(4 + total_participants, 2, total_line, color_total)


        stdscr.addstr(6 + total_participants, 2, "Press SPACE to switch, A to add a participant.", curses.A_BOLD)
        stdscr.refresh()

        # Check for spacebar to move to next participant
        key = stdscr.getch()
        if key == ord(' '):
            # Freeze the current participant's state in finished_states
            if current_participant < total_participants:
                # Compute final snapshot for current participant
                elapsed = now - participant_starts[current_participant]
                remaining = participant_share[idx] - elapsed
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
                finished_states[current_participant] = {
                    'disp_time': disp_time,
                    'bar': bar,
                    'color': color
                }
                current_participant += 1
                if current_participant < total_participants:
                    participant_starts[current_participant] = now

        elif key in (ord('a'), ord('A')):
            # Add a participant if it does not exceed max participants
            if total_participants < max_participants:
                total_participants += 1
                participant_starts.append(now)
                participant_times.append(participant_secs)  # placeholder; will be updated below
                participant_share.append(participant_secs)  # placeholder; will be updated below
                finished_states.append(None)
                # Recalculate remaining time allocation for the active and future participants.
                remaining_meeting = max(total_meeting_secs - total_elapsed, 0)
                num_slots = total_participants - current_participant  # active one included
                new_alloc = remaining_meeting / num_slots if num_slots > 0 else 0
                for i in range(current_participant, total_participants):
                    participant_times[i] = new_alloc
                    participant_share[i] = new_alloc

        time.sleep(0.1)

    # End meeting screen message
    stdscr.addstr(1, 2, "Meeting complete. Press x to exit.", curses.A_BOLD)
    stdscr.refresh()
    stdscr.nodelay(False)
    while True:
        key = stdscr.getch()
        if key in (ord('x'), ord('X')):
            break

def main():
    args = sys.argv[1:]
    if len(args) >= 2:
        try:
            total_time = float(args[0])
            participants = int(args[1])
            skip_confirmation = True
        except ValueError:
            print("Invalid command-line arguments. Falling back to interactive mode.")
            print("Usage: python yast2.py <total_meeting_time_in_minutes> <number_of_participants>")
            total_time = None
            participants = None
            skip_confirmation = False
    else:
        total_time = None
        participants = None
        skip_confirmation = False

    if total_time is None:
        try:
            print("Usage: python yast2.py <total_meeting_time_in_minutes> <number_of_participants>")
            print("Falling back to interactive mode.")
            total_time = float(input("Enter total meeting time (in minutes): "))
        except ValueError:
            print("Invalid input, please enter a number.")
            return

    if participants is None:
        try:
            participants = int(input("Enter number of participants: "))
        except ValueError:
            print("Invalid input, please enter an integer.")
            return

    if not skip_confirmation:
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