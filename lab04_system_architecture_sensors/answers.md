# Lab 4 Answers

## Selected-sensor interface

Use the same sensor throughout the interface inspection, data-flow trace, and TF explanation.

| ROS topic | Message type | Numeric field and SI unit | Message frame ID | Two measurement timestamps | Approximate rate over at least 10 s | Observed consumer |
|---|---|---|---|---|---|---|
| | | | | | | |

Do timestamps advance while Gazebo runs? Note gaps or pauses. Distinguish measurement timestamps from message arrival timing.

## Coordinate-frame interpretation

Record the selected sensor's frame chain from `map` to its message frame. Identify moving and fixed relationships. Also identify the base frame and at least two sensor frames in RViz2.

Explain how the consumer places the measurement on the map at its timestamp. What would fail if the mounting transform were missing or the required timestamp were outside the available transform history?

## Student-selected data-flow trace

Complete the prediction columns before inspecting the topic endpoints. Complete the evidence columns afterward.

| Selected ROS topic | Predicted simulated source | Bridge predicted? Why? | Predicted ROS consumer | Pause behavior predicted | Observed publisher/bridge/consumer evidence | Observed pause behavior |
|---|---|---|---|---|---|---|
| | | | | | | |

Explain one part of your original prediction that the ROS or Gazebo graph confirmed or corrected.

## Sensor-to-function mapping

Insert the required table from Part 5.

## Engineering questions

Answer Questions 1–5 from the README. Include the sensing-to-actuation block diagram requested in Question 5. Label the selected sensor source, any bridge, topic, observed consumer, and the roles of localization, planning, control, TF, and timestamps. Distinguish observed connections from conceptual relationships.
