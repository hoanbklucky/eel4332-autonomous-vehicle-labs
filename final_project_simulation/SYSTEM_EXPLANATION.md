# Individual final project report

**Name** — [Your name]  
**GitHub repository** — [Link]

[Download the editable Word template](Goosebot_Final_Project_Report_Template.docx).

Replace the bracketed text with results from your own runs. Add one or two sentences explaining what each result shows.

## Steps 4–5 · IST mapping

[Paste a screenshot of your saved IST map in RViz.]

[Describe the part of IST you mapped and point out a feature you recognize in the map.]

## Step 6 · IST navigation

[Paste a screenshot or a short result excerpt from your AMCL navigation run.]

[Name your two destinations and say whether Goosebot reached each one and returned Home.]

## Step 9 · Raw sensor readings

[Paste a short excerpt from one message for each source. For LiDAR, a few range values are enough.]

| Source | ROS 2 topic | Short reading excerpt |
|---|---|---|
| Ordinary GPS | [Topic] | [Reading] |
| RTK-like GPS | [Topic] | [Reading] |
| IMU | [Topic] | [Reading] |
| Wheel joint states | [Topic] | [Reading] |
| LiDAR | [Topic] | [Reading] |

[Briefly describe what you see in the readings. For example, point out the latitude and longitude in a GPS message.]

## Step 9 · ROS 2 node graph

[Paste your node graph screenshot. Label `/wheel/odometry` and `/imu/data` entering the local EKF.]

[Describe one connection shown in your graph.]

## Step 9A · Localization accuracy

[Paste your comparison plot and the error table for the unmodified drive.]

[Say which of the three estimates had the lowest position error and cite a value from your table. Briefly note whether the controlled case changed your conclusion.]

## Step 9B · Campus navigation

[Paste a screenshot showing Goosebot and its planned route on the supplied pedestrian-only map, or a short result excerpt from your run.]

[Say whether Goosebot reached A, B, and Home. Describe one thing you noticed about the route.]

## How mapping and navigation work

**Indoors in IST** — [In your own words, explain how LiDAR and SLAM Toolbox helped Goosebot build the map. Then explain how AMCL and Nav2 used your saved map to locate Goosebot and drive to a goal.]

**Outdoors on campus** — [In your own words, explain how Goosebot used the supplied pedestrian-only map, RTK-like GPS, and live LiDAR to locate itself, plan a route, and avoid obstacles. What was different about how the map was obtained?]

## Brief reflection

[In a few sentences, reflect on what you learned from building the IST map, using the supplied campus map, and navigating in both places.]

## How the 50% report component is assessed

| Criterion | Project percentage points |
|---|---:|
| IST map and explanation | 10 |
| Raw sensor readings and labeled node graph | 10 |
| One-drive localization accuracy comparison | 15 |
| Indoor and outdoor navigation results | 5 |
| System explanation and reflection | 10 |
