# Yet Another Standup Timer Tool (yast2)

![Daily Standup Planner](doc/img/2025-02-13%2021_59_52-yast2.py%20-%20yast2%20-%20Visual%20Studio%20Code.png)

This project is a simple command-line application designed to facilitate Scrum daily standup meetings. It allows users to input the total meeting time, the number of participants, and checks if the meeting is ready to start. The application calculates the time allocated for each participant and features a countdown timer with a progress bar that visually indicates the time remaining.

![Running the application](doc/img/2025-02-13%2022_00_18-yast2.py%20-%20yast2%20-%20Visual%20Studio%20Code.png)

It is written in Python and uses the `curses` library for terminal display.

## Features

- User input for total meeting time and number of participants.
- Calculation of time per participant.
- Countdown timer with a progress bar that changes color based on time remaining.
- Ability to switch between participants using the space key.

## Installation

To get started with the Scrum Daily Standup Planner, follow these steps:

1. Clone the repository:
   ```
   git clone ...
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