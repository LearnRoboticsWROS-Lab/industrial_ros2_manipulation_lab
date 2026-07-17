# Tests

| Test | What it verifies | Requirements |
|---|---|---|
| `test_mock_cycle.sh` | the full pick-and-place cycle against mock backends (13 stages, SUCCESS) | a built workspace; no Gazebo, no hardware |

Run inside the container:

    bash tests/test_mock_cycle.sh

This is also the pattern for capstone CI: task logic verified headless in mock
mode on every change.
