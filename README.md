# Decentralized Graph Coloring using ABT

This program is a visualization of the Asynchronous Backtracking Algorithm being applied to the Graph Coloring Problem. Given a graph and
a set of colors, the Graph Coloring Problem asks the question, "Can each node of the graph be colored one of the provided colors such that
no two neighboring nodes share the same color, and if yes, what is one such coloring of the graph?". This program uses to Asynchronous
Backtracking Algorithm to solve the Graph Coloring Problem in a decentralized manner. More precisely, each node is only aware of its own
color and the colors of its neighbors, and each node is only able to communicate (through messages) with its neighbors.

![alt-text](./ABT%201.png)

In the visualization, messages of different colors represent different kinds of messages:

* **Green:** "Ok?" messages - contains the sender's agent number and their color
* **Red:**   "No good" messages - contains the sender's agent_view
* **Turqoise:** "Connection Request" messages - searches for a specific agent to add an indirect link with
* **Dark Blue:** "Connection Successful" messages - returns to agent that sent the connection request to complete indirect link
* **Black:** "No solution" messages - broadcasts to all neighboring agents that there is no solution

In order to run the visualization, run ``main.py``. Change ``EXAMPLE`` and ``NUM_COLORS`` in ``main.py`` to test different example graph coloring problems. If trying to create a new example, store the graph matrix in ``graph_matrix`` and the relative positions of each of the nodes in ``positions``.
