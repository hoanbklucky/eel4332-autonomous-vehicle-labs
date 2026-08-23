# ROS 2 Fundamentals — Part 1: Graph and Communication

[Lab 00 setup](README.md) | [Part 2: Packages, Workspaces, and Launch](ros2_fundamentals_part2.md)

## Purpose

Complete Part 1 before Part 2. It introduces the ROS graph and the four interaction patterns students will use throughout the course: topics, services, actions, and parameters. Allow approximately 45–60 minutes.

Run **one command block at a time** and examine its output before continuing. After running a command, expand **Expected output** to compare your result with the example screenshot. Do not copy an entire practice section into the WSL/Ubuntu Terminal at once. Commands split across two displayed lines with a trailing `\` are one command, not two commands.

The official [ROS 2 Jazzy beginner CLI tutorials](https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools.html) provide additional explanations and examples.

Most ROS 2 commands follow this pattern:

```text
ros2 <command group> <operation> [name] [options]
```

For example, in `ros2 topic list -t`, `topic` selects the topic command group, `list` selects the operation, and `-t` requests type information. Names beginning with `/`, such as `/chatter`, identify resources in the live ROS graph. Press the `Tab` key while typing to explore available commands and names.

## Mental Model

ROS 2 is middleware and a collection of development tools, not a simulator or a robot model.

| Term | Meaning | Typical autonomous-vehicle example |
|---|---|---|
| node | one running ROS program or component | LiDAR driver or planner |
| topic | asynchronous stream for continuous data | laser scans or velocity commands |
| message | typed data carried by a topic | `sensor_msgs/msg/LaserScan` |
| service | short request followed by one response | reset or configuration request |
| action | longer operation with feedback and cancellation | navigate to a goal |
| parameter | named configuration value owned by a node | update rate or frame name |
| launch file | reproducible description for starting nodes together | simulator and navigation bringup |
| package | installable unit containing ROS code and metadata | `nav2_bringup` |
| workspace | directory in which one or more packages are built | `~/eel4332_ws` |

Topics suit continuous streams, services suit quick request/response operations, and actions suit longer, cancelable tasks that report feedback. Do not select an interface only by its name; inspect its type and communication pattern.


## Communication Patterns at a Glance

The arrows below show who initiates each interaction and what information returns. These patterns solve different problems; none is a universally better replacement for the others.

```mermaid
flowchart LR
    publisher["Publisher node"] -->|"messages continuously"| topic(["Topic"])
    topic -->|"messages continuously"| subscriber["Subscriber node"]

    service_client["Service client"] -->|"one request"| service_server["Service server"]
    service_server -->|"one response"| service_client

    action_client["Action client"] -->|"goal"| action_server["Action server"]
    action_server -->|"feedback while running"| action_client
    action_server -->|"final result"| action_client

    parameter[("Parameter value")] -.->|"configures"| owner["Owning node"]
```

- A **topic** carries an asynchronous stream; publishers do not wait for subscribers to reply.
- A **service** handles a short request and returns one response.
- An **action** handles a longer, cancelable goal and can return feedback before its result.
- A **parameter** is a configuration value owned by a node; it is not a communication stream.

Use the diagram as a map while completing the practices. The command output and screenshots show how each relationship appears in a running ROS graph.

## Practice 1 — Source ROS in Every WSL/Ubuntu Terminal

Open a WSL/Ubuntu Terminal and run:

```bash
source /opt/ros/jazzy/setup.bash
```

Confirm the selected ROS distribution:

```bash
echo "$ROS_DISTRO"
```

Locate the ROS 2 command:

```bash
which ros2
```

The expected distribution is `jazzy`, and `which ros2` should resolve to `/opt/ros/jazzy/bin/ros2`.

`source` changes the environment of the current shell only. Every newly opened WSL/Ubuntu Terminal must source ROS, either manually or through `~/.bashrc`. Commands entered at a PowerShell prompt are not Ubuntu commands; enter `wsl` first.

## Practice 2 — Run and Inspect Publisher/Subscriber Nodes

The system in this practice has the following intended ROS graph:

```mermaid
flowchart LR
    talker["Node: /talker"]
    chatter(["Topic: /chatter<br/>Type: std_msgs/msg/String"])
    listener["Node: /listener"]
    cli["Temporary CLI publisher<br/>ros2 topic pub"]

    talker -->|publishes message instances| chatter
    chatter -->|delivers message instances| listener
    cli -.->|publishes one message| chatter
```

Read the graph from left to right:

- `/talker` and `/listener` are running nodes;
- `/chatter` is the named communication channel connecting them;
- `std_msgs/msg/String` is the message **type** allowed on that topic;
- each numbered `Hello World` value is one message **instance** moving through the topic;
- `ros2 topic pub` creates a temporary command-line publisher, shown with a dashed connection;
- the listener and its connection do not exist until you start the listener node.

The graph shows communication relationships, not the order in which terminal windows were opened. A topic is not a program, and a message is not a permanent graph component. Use `rqt_graph` to visualize live connections, and use the ROS CLI to inspect message types, fields, rates, and Quality of Service details that the graph does not show.

Open three WSL/Ubuntu Terminals.

In **WSL/Ubuntu Terminal 1**, start a publisher:

```bash
source /opt/ros/jazzy/setup.bash
```

```bash
ros2 run demo_nodes_py talker
```

**Command breakdown:** `run` starts one executable from an installed package. Here, `demo_nodes_py` is the package and `talker` is the executable. The executable creates a node named `/talker` and keeps running until you press `Ctrl+C`.

<details>
<summary>Expected output</summary>

![The demo talker publishing numbered Hello World messages](images/practice2-01-talker-publishing.png)

*Expected talker output. The node publishes a new numbered string approximately once per second.*

</details>

Keep it running. In **WSL/Ubuntu Terminal 2**, inspect the graph:

```bash
source /opt/ros/jazzy/setup.bash
```

List the running nodes:

```bash
ros2 node list
```

**Command breakdown:** `node list` asks the ROS graph for the names of all currently discoverable nodes. It does not start or stop anything.

<details>
<summary>Expected output</summary>

![The ROS node list containing the talker node](images/practice2-02-node-list.png)

*The running publisher appears as the `/talker` node.*

</details>

Inspect the talker node:

```bash
ros2 node info /talker
```

**Command breakdown:** `node info` inspects one named node. `/talker` is the node name; the output shows its publishers, subscribers, services, and actions.

<details>
<summary>Expected output</summary>

![Detailed ROS information for the talker node](images/practice2-03-node-info-talker.png)

*Node information identifies the talker's publishers, service servers, and other interfaces.*

</details>

List topics together with their message types:

```bash
ros2 topic list -t
```

**Command breakdown:** `topic list` prints the currently discoverable topic names. The `-t` option adds the message type associated with each topic.

<details>
<summary>Expected output</summary>

![ROS topic list showing chatter and its String message type](images/practice2-04-topic-list-types.png)

*The `/chatter` topic carries `std_msgs/msg/String` messages.*

</details>

Inspect the publishers, subscribers, type, and Quality of Service settings for `/chatter`:

```bash
ros2 topic info /chatter --verbose
```

**Command breakdown:** `topic info` examines one topic. `/chatter` is the topic name, and `--verbose` adds endpoint details such as node names, publisher and subscriber counts, and Quality of Service settings.

<details>
<summary>Expected output</summary>

![Verbose chatter topic information with one publisher and no subscribers](images/practice2-05-topic-info-publisher.png)

*Before the listener starts, `/chatter` has one publisher and no subscribers.*

</details>

Inspect the fields in the message type:

```bash
ros2 interface show std_msgs/msg/String
```

**Command breakdown:** `interface show` prints the definition of a ROS interface type. `std_msgs/msg/String` means the `String` message in the `msg` directory of the `std_msgs` package.

<details>
<summary>Expected output</summary>

![The std_msgs String interface containing its data field](images/practice2-06-string-interface.png)

*The message definition contains one string field named `data`.*

</details>

Display one message and return to the prompt:

```bash
ros2 topic echo /chatter --once
```

**Command breakdown:** `topic echo` temporarily subscribes to `/chatter` and prints received messages. The `--once` option exits after the first message instead of continuing indefinitely.

<details>
<summary>Expected output</summary>

![One numbered Hello World message echoed from chatter](images/practice2-07-topic-echo-once.png)

*The `--once` option prints one message and then returns to the shell prompt.*

</details>

Measure the publication rate:

```bash
ros2 topic hz /chatter
```

**Command breakdown:** `topic hz` temporarily subscribes to `/chatter`, measures message arrival times, and reports the estimated frequency in hertz. It continues until you press `Ctrl+C`.

<details>
<summary>Expected output</summary>

![Measured chatter topic rate of approximately one hertz](images/practice2-08-topic-rate.png)

*The measured average rate is approximately `1 Hz`, matching the talker's behavior.*

</details>

Let `ros2 topic hz` collect data for approximately 10 seconds and then press `Ctrl+C`.

In **WSL/Ubuntu Terminal 3**, start a subscriber:

```bash
source /opt/ros/jazzy/setup.bash
```

```bash
ros2 run demo_nodes_py listener
```

**Command breakdown:** this uses `run` again, now starting the `listener` executable from `demo_nodes_py`. It creates the `/listener` node, which subscribes to `/chatter`.

<details>
<summary>Expected output</summary>

![The demo listener receiving numbered Hello World messages](images/practice2-09-listener-running.png)

*The listener subscribes to `/chatter` and prints each received message.*

</details>

Return to WSL/Ubuntu Terminal 2 and inspect the topic again:

```bash
ros2 topic info /chatter --verbose
```

**Command breakdown:** repeat the verbose inspection after starting `/listener`. Comparing the two outputs reveals that the subscriber count changed from zero to one.

<details>
<summary>Expected output</summary>

![Verbose chatter information with one publisher and one subscriber](images/practice2-10-topic-info-publisher-subscriber.png)

*After the listener starts, the topic has one publisher and one subscriber.*

</details>

Confirm that the graph now contains a publisher and a subscriber. Notice that a topic is not a process: nodes publish or subscribe to a named, typed topic.

Visualize the live graph from WSL/Ubuntu Terminal 2:

```bash
rqt_graph
```

When the `rqt_graph` window opens:

1. Make sure both the `/talker` and `/listener` nodes are still running.
2. Open the drop-down menu near the upper-left corner and select **Nodes/Topics (all)**.
3. Click the **Refresh** button (the circular-arrow icon at the far left of the toolbar).

The graph area may initially be empty. Selecting **Nodes/Topics (all)** and clicking **Refresh** forces `rqt_graph` to rediscover and display the current ROS graph. Confirm that it contains:

<details>
<summary>Expected output</summary>

![rqt_graph showing the talker publishing to chatter and the listener subscribing to chatter](images/practice2-rqt-graph.png)

*The live graph after selecting **Nodes/Topics (all)** and clicking **Refresh**.*

</details>

```text
/talker → /chatter → /listener
```

Compare it with the conceptual graph above. The temporary CLI tools used by `ros2 topic echo` or `ros2 topic hz` may appear only while those commands are running. Close `rqt_graph` before continuing.

Stop the talker with `Ctrl+C`, but keep the listener running. Publish one message manually from WSL/Ubuntu Terminal 2:

```bash
ros2 topic pub --once /chatter std_msgs/msg/String \
  "{data: 'hello from the EEL 4332 command line'}"
```

**Command breakdown:** `topic pub` creates a temporary publisher. `--once` sends one message, `/chatter` is the destination topic, `std_msgs/msg/String` is its required type, and the YAML expression supplies the `data` field. The trailing `\` only continues the same shell command on the next displayed line.

<details>
<summary>Expected output</summary>

![A manually published String message sent to chatter](images/practice2-11-manual-publish.png)

*The command-line publisher sends one correctly typed message.*

</details>

Confirm that the listener receives it:

<details>
<summary>Expected output</summary>

![The listener receiving the manually published EEL 4332 message](images/practice2-12-listener-receives-manual-message.png)

*The final listener line confirms that the manually published message traveled through `/chatter`.*

</details>

Then stop the listener.

## Practice 3 — Services, Parameters, and Actions

In WSL/Ubuntu Terminal 1, start turtlesim:

```bash
source /opt/ros/jazzy/setup.bash
```

```bash
ros2 run turtlesim turtlesim_node
```

**Command breakdown:** `run` starts the `turtlesim_node` executable from the installed `turtlesim` package. The process creates a node named `/turtlesim` and opens the graphical simulator window.

<details>
<summary>Expected output</summary>

![The turtlesim window with the original turtle near the center](images/practice3-01-turtlesim-start.png)

*The turtlesim node opens a graphical window containing the original turtle.*

</details>

### Inspect and call a service

In WSL/Ubuntu Terminal 2:

```bash
source /opt/ros/jazzy/setup.bash
```

List available services and their types:

```bash
ros2 service list -t
```

**Command breakdown:** `service list` prints the names of currently available services. The `-t` option also shows the service type required by each service.

<details>
<summary>Expected output</summary>

![List of available ROS services and their service types](images/practice3-02-service-list.png)

*The list includes `/spawn` with the service type `turtlesim/srv/Spawn`.*

</details>

Show the type of the `/spawn` service:

```bash
ros2 service type /spawn
```

**Command breakdown:** `service type` looks up the interface type used by one service. `/spawn` is the service name; its returned type is needed to inspect or call it.

<details>
<summary>Expected output</summary>

![The service type returned for the spawn service](images/practice3-03-spawn-service-type.png)

*The command confirms the type required when calling `/spawn`.*

</details>

Inspect the request and response fields:

```bash
ros2 interface show turtlesim/srv/Spawn
```

**Command breakdown:** `interface show` prints the `Spawn` service definition from the `turtlesim` package. The `srv` portion identifies it as a service interface. The `---` line separates request fields from response fields.

<details>
<summary>Expected output</summary>

![Request and response fields of the turtlesim Spawn service](images/practice3-04-spawn-interface.png)

*Fields above `---` belong to the request; fields below it belong to the response.*

</details>

Call the service:

```bash
ros2 service call /spawn turtlesim/srv/Spawn \
  "{x: 2.0, y: 2.0, theta: 0.0, name: 'practice_turtle'}"
```

**Command breakdown:** `service call` sends one request to `/spawn`. The next argument declares the expected service type, and the YAML expression supplies values for its request fields. The command waits for and then prints the response.

<details>
<summary>Expected output</summary>

![Successful call to the turtlesim spawn service](images/practice3-05-spawn-service-call.png)

*A successful response returns the name assigned to the new turtle.*

</details>

A second turtle should appear. The request contains input fields; the service returns one response.

<details>
<summary>Expected output</summary>

![The turtlesim window after spawning practice turtle](images/practice3-06-turtlesim-after-spawn.png)

*The new turtle appears at the requested position while the original turtle remains in the simulation.*

</details>

### Inspect and change a parameter

```bash
ros2 param list /turtlesim
```

**Command breakdown:** `param list` prints the parameter names owned by the `/turtlesim` node. Parameters are node-specific configuration values.

<details>
<summary>Expected output</summary>

![Parameters owned by the turtlesim node](images/practice3-07-param-list.png)

*The output includes the configurable background color components and other turtlesim parameters.*

</details>

```bash
ros2 param get /turtlesim background_r
```

**Command breakdown:** `param get` reads one parameter. `/turtlesim` identifies the node and `background_r` identifies its red-background component.

<details>
<summary>Expected output</summary>

![Current value of the turtlesim background red parameter](images/practice3-08-param-get-background-r.png)

*The command reports the parameter type and its current value. The initial value may differ between installations.*

</details>

```bash
ros2 param set /turtlesim background_r 100
```

**Command breakdown:** `param set` requests a new value for a node parameter. It asks `/turtlesim` to change `background_r` to `100` and reports whether the update succeeded.

<details>
<summary>Expected output</summary>

![Successful update of the turtlesim background red parameter](images/practice3-09-param-set-background-r.png)

*`Set parameter successful` confirms that the node accepted the new value.*

</details>

Parameters configure a node. They are not intended to replace a high-rate sensor or command topic.

### Inspect and send an action goal

```bash
ros2 action list -t
```

**Command breakdown:** `action list` prints available action names. The `-t` option adds each action's interface type.

<details>
<summary>Expected output</summary>

![Available turtlesim actions and their interface types](images/practice3-10-action-list.png)

*Each turtle has a `rotate_absolute` action using the `turtlesim/action/RotateAbsolute` type.*

</details>

```bash
ros2 action info /turtle1/rotate_absolute
```

**Command breakdown:** `action info` inspects an action endpoint. It reports the action type and the nodes acting as action clients or servers for `/turtle1/rotate_absolute`.

<details>
<summary>Expected output</summary>

![Information about the turtle1 rotate absolute action](images/practice3-11-action-info.png)

*The `/turtlesim` node provides one action server; no action client exists until a goal is sent.*

</details>

```bash
ros2 action send_goal /turtle1/rotate_absolute \
  turtlesim/action/RotateAbsolute "{theta: 1.57}" --feedback
```

**Command breakdown:** `action send_goal` sends a goal to the named action using the stated action type. The YAML expression requests an absolute heading of `1.57` radians, approximately 90 degrees. `--feedback` prints progress messages while the goal is executing, followed by the final result.

<details>
<summary>Expected output</summary>

![An accepted rotate action goal followed by progress feedback](images/practice3-12-action-send-goal.png)

*The server accepts the goal and reports the remaining rotation as feedback. Goal identifiers and numeric feedback values will vary between runs.*

</details>

Observe the feedback while the turtle rotates. An action is appropriate because the operation takes time and has a goal, feedback, and final result.

Stop turtlesim with `Ctrl+C`.

## Part 1 Completion Check

Before continuing to Part 2, confirm that you can:

- [ ] distinguish nodes, topics, messages, services, actions, and parameters;
- [ ] explain the `/talker → /chatter → /listener` graph;
- [ ] distinguish a message type from one message instance;
- [ ] inspect a running graph with ROS CLI tools and `rqt_graph`;
- [ ] publish a correctly typed message from the command line;
- [ ] call a service, change a parameter, and send an action goal.

Continue to [Part 2 — Packages, Workspaces, and Launch](ros2_fundamentals_part2.md).
