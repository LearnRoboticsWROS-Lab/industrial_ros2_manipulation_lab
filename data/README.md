# Data Directory

This folder holds recorded and replayed data used by the lab, so that every
perception lesson can be completed **without real hardware**.

| Folder | Content | Used by |
|---|---|---|
| `rosbags/` | Recorded ROS2 bag files (camera streams, TF, detections) for replay | Module 6, Module 9 study material |
| `images/` | Sample RGB and depth images from the simulated camera | Module 6 vision lessons |
| `pointclouds/` | Sample point cloud files (.pcd) | Module 6 PCL lessons |
| `detections/` | Recorded object detection results (poses, labels, confidences) | Perception mock replay, Module 6/7 |

## Notes

- Large payloads are git-ignored; the folders are kept with `.gitkeep`.
- The perception mock (`src/lrwros_perception_mock/`) can replay data from
  `detections/` so the whole vision-guided pipeline runs with no camera at all.
- If you record your own data, keep file names descriptive:
  `<scene>_<object>_<date>.bag`.
