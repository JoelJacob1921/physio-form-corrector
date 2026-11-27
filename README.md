# Physio Form Corrector

A tool that uses your webcam to check your form during physiotherapy exercises and give feedback in real time.

## Project goal

Most people do their physio exercises alone at home with no one checking their form. This project uses a webcam and pose detection to track the body, count reps, and tell the user when their form is off.

## MVP scope

The first version covers one exercise, the squat, filmed from the side:

- Live webcam feed with a skeleton overlay
- Knee and back angle calculation
- Rep counting
- Simple feedback like "Go deeper" or "Keep your chest up"
- Summary of reps and form at the end of a set

## Future plans

- Have a physical therapist check the angle thresholds
- Add a second exercise (shoulder raise or lunge)
- Save session history and track progress
- Add audio cues

## Tech stack

Python, OpenCV, MediaPipe Pose, NumPy, pytest

## Setup

Requires Python 3.9+ (tested on macOS, Apple Silicon).

```bash
git clone https://github.com/JoelJacob1921/physio-form-corrector.git
cd physio-form-corrector
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install --no-compile -r requirements.txt
```

> `--no-compile` is needed because MediaPipe 1.2.3 ships with a typo in one of its own internal test files, which crashes pip's compile step. Skipping that step is safe; Python compiles the files it actually uses on first run.

## Diagrams

- System diagram: ![System diagram](docs/system_diagram.png)
- [Eisenhower Matrix (PDF)](docs/eisenhower_matrix.pdf)
