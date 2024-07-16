![image](https://github.com/user-attachments/assets/c6d7849f-39d8-4040-ac57-cacf62c21e54)

# Sand Simulation
Sand simulation made with pygame.

In this sand simulation you can spawn up to 5 materials: **Sand, Water, Stone, Fire, Wood**. They interact and behave with each other in different ways, try it yourself!

![sand_simulation](https://github.com/user-attachments/assets/66d8e51d-f1b1-4212-bf38-e871c1165666)

# Installation to run

To run the simulation first download [python](https://www.python.org/downloads/) if you don't have it.

Then download the repository and install the dependencies, inside the simulation folder, with:

```
pip install -r requirements.txt
```

Finally run the simulation with:

```
python3 main.py
```

# Controls

- Spawn material:
    - `mouse-left-click`: spawns the selected material

- Select material:
    - `1`: selects **Sand**
    - `2`: selects **Water**
    - `3`: selects **Stone**
    - `4`: selects **Fire**
    - `5`: selects **Wood**

- Brush size:
    - `mouse-wheel-up`: enlarge the brush radius
    - `mouse-wheel-down`: shrink the brush radius

- Delete with brush:
    - `mouse-right-click`: deletes with brush

- Delete all:
    - `r`: Deletes all the canvas

### DEBUG

- Print the selected cell info:
    - If *debug* mode is active, `mouse-middle-click` prints the selected cells info.
