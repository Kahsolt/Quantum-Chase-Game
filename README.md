# ArcLight-2023-Quantum-Game

    弧光量子云 第一届量子信息技术与应用创新大赛—基于量子计算机的游戏设计

----

contest page: [https://qcloud.arclightquantum.com/#/competition/introduction](https://qcloud.arclightquantum.com/#/competition/introduction)


### gameplay

In brief, there are 3 stages for a complete gaming routine:

- stage 0: QFC
    - two players join the same room, starts the game
    - each player choose a bit on their own, perform [Quantum Coin Flipping](https://en.wikipedia.org/wiki/Quantum_coin_flipping) based on the [Quantum Bit Escrow](https://arxiv.org/pdf/quant-ph/0004017.pdf) protocol to decide the game role (Alice/Bob); swicth to stage 1
- stage 1: QTL
    - you are a wandering qubit, moving on the [Bloch Sphere](https://en.wikipedia.org/wiki/Bloch_sphere) use W/A/S/D key, and collecting the randomly spawned **photons** and **quantum gates**
    - the more photons you hold, the faster your moving speed :)
    - cost quantum gates to make a quick position transport
    - your partener is also wandering on the ball but you cannot see him/her, you can cost photons to measure his/her qubit state through [Quantum Teleportation](https://en.wikipedia.org/wiki/Quantum_teleportation), this will highliht his/her latitude on the ball
    - when two players meets closely nearby, they become visible to each other; swicth to stage 2
- stage 2: VQE
    - ???


### how to run

- see REAME.md in both [server](server/README.md) and [client](cleint/README.md) folder

----
by Armit
2023/09/05
