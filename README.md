# raft-py
[![Build Status](https://travis-ci.com/mdmiller002/raft-py.svg?branch=master)](https://travis-ci.com/mdmiller002/raft-py)

A Python 3 implementaiton of the Raft consensus algorithm


## What is Raft
Raft is a distributed consensus algorithm that ensures fault tolerance
and consistency, while maintaining understandability. There are many
resources on Raft, e.g.: [raft.github.io](https://raft.github.io/)

### The consensus algorithm
In short, a node can be one of three states:
1. Follower
2. Candidate
3. Leader

When a node is a follower, it generates a random timeout and waits.
If a follower does not hear a heartbeat from its leader in the timeout
period, it enters the candiate state.

When a node is a candidate, it sends vote requests to the other nodes.
If a follower has not voted in the current election term (more on that
later) then the follower sends back a vote. A candidate either becomes
leader by getting a majority of votes, or falls back to follower
if it can't get enough votes within the candidate timeout.

When a node is a leader, it sends heartbeats to the followers.

### Election Terms
A mechanism called election terms is used to maintain consistency
in Raft. Essentially, each time a follower moves to the candidate
state it enters a new election term (an increasing non-negative number).
Election terms are used in the algorithm for several things, like
maintaining consistency in the event of network partitions.

### A note on logs
Logs are used in raft to distribute state changes throughout the cluster.
This implementation currently does implement the log portion of the algorithm.
