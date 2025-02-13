# Yet Another Standup Timer Tool (yast2)

![Daily Standup Planner](doc/img/2025-02-13%2021_59_52-yast2.py%20-%20yast2%20-%20Visual%20Studio%20Code.png)

This project is a simple command-line application designed to facilitate Scrum daily standup meetings. It allows users to input the total meeting time, the number of participants, and checks if the meeting is ready to start. The application calculates the time allocated for each participant and features a countdown timer with a progress bar that visually indicates the time remaining.

![Running the application](doc/img/2025-02-13%2023_24_24-README.md%20-%20yast2%20-%20Visual%20Studio%20Code.png)

It is written in Python and uses the `curses` library for terminal display.

Pressing SPACE will switch between participants.

Pressing A will add late-coming participants on the fly, redistributing the remaining time among the current and new participants.

The countdown is displayed in minutes and seconds, with the progress bar changing color based on the time remaining:

- Green: More than 75% of the allocated time for the participant remaining.
- Yellow: Less than 25% of the allocated time for the participant remaining.
- Red: **overtime** - the bar turns red and will fill up from the right to the left. The timer will start to count up to show how much additional time the participant has used. If the bar is full (the participant has used more than double their allocated time), the bar will not change anymore but the timer will continue counting up.

The originally allotted time is displayed beneath the progress bars along with the total elapsed time. This line will change to red if the total elapsed time exceeds the total meeting time.

## Features

- User input for total meeting time and number of participants.
- Calculation of time per participant.
- Countdown timer with a progress bar that changes color based on time remaining.
- Overtime tracking for participants.
- Switch between participants using the space key.
- Add late-coming participants on the fly and redistribute remaining time.


## Installation

To get started with yet another standup timer tool,
 follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/Agh42/yast2.git
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the application, execute the following command in your terminal:

```
python yast2.py
```

Follow the prompts to enter the total time for the meeting, the number of participants, and confirm when the meeting is ready to start.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, feel free to open an issue or submit a pull request.