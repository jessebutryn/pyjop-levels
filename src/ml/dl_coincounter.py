### INIT CODE - DO NOT CHANGE ###
from pyjop import *
from types import SimpleNamespace

SimEnv.connect()
editor = LevelEditor.first()
### END INIT CODE ###

### IMPORTS - Add your imports here ###
import random
### END IMPORTS ###

### DATA MODEL - Define a data model needed for this custom level to share data between function calls ###

NUM_RUNS = 5

COINS = {
    "CoinEuroCent1":1,
    "CoinEuroCent2":2,
    "CoinEuroCent20":20,
    "CoinEuroCent50":50,
    "CoinEuro1":100
}

class DataModel(DataModelBase):
    def __init__(self) -> None:
        super().__init__()
        self.num_correct = 0
        self.num_incorrect = 0
        self.sum = 0
        self.train_sum = 0
        self.train_count = 0
        self.count = 0

    def spawn_next(self):
        editor.destroy_temporaries()
        sleep()
        self.sum = 0
        self.train_sum = 0
        self.train_count = 0
        self.count = 0

        for dattype in ("train","test"):
            ct = random.randint(5,16)
            if dattype == "train":
                self.train_count = ct
            else:
                self.count = ct
            idx = sorted(list(range(16)), key=lambda x: random.random())[0:ct]
            
            for i in range(0, 16):
                if i not in idx:
                    continue
                cname,cval = random.choice(list(COINS.items()))
                if dattype=="test":
                    self.sum += cval
                else:
                    self.train_sum += cval
                x = (i % 4 - 1.5) / 1.5  * 1.2
                y = (i //4 - 1.5) / 1.5  * 1.2
                xloc = 4 if dattype=="test" else -4
                editor.spawn_static_mesh(SpawnableMeshes(cname), simulate_physics=False, is_temp=True, location = (xloc + x + random.uniform(-0.15,0.15),0.150 + y + random.uniform(-0.15,0.15),0.2), rotation = (0,0, random.uniform(-180,180)), scale=2, adjust_z=True)
        InputBox.find("train_coin_result").set_text(str(self.train_sum))
        InputBox.find("coin_result").set_text("")
        InputBox.find("coin_result").editor_set_hint_text(f"Enter coin sum...")
        #editor.set_color("train_background", random.choice([Colors.Purple, Colors.Red, ]))
        #print(self.sum)

data = DataModel()
### END DATA MODEL ###


### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.select_map(SpawnableMaps.BrutalistHall)
editor.spawn_entity(SpawnableEntities.SmartCamera, "cam", location=(3.85, 0.15, 3.75), rotation=(0,-90,0))
editor.spawn_entity(SpawnableEntities.InputBox, "coin_result", (4.0, 3.0, 0.5))
editor.spawn_static_mesh(SpawnableMeshes.Cube, scale= (3.5,3.5,0.2), location=(4, 0.15, 0), material=SpawnableMaterials.SimpleColor, color=Colors.Green)

editor.spawn_entity(SpawnableEntities.SmartCamera, "train_cam", location=(-4.15, 0.15, 3.75), rotation=(0,-90,0))
editor.spawn_entity(SpawnableEntities.ObjectSpawner, "train_spawn", location=(-4.3, 0.15, 5.25), rotation=(0,0,-90))
editor.spawn_static_mesh(SpawnableMeshes.Cube, "train_background", scale= (3.5,3.5,0.2), location=(-4, 0.15, 0), material=SpawnableMaterials.SimpleColor, color=Colors.Green)
editor.spawn_entity(SpawnableEntities.InputBox, "train_coin_result", (-4.0, 3.0, 0.5))
# i = 0
# for cname,val in COINS.items():
#     x = (i % 4 - 1.5) / 1.5  * 1.2
#     y = (i //4 - 1.5) / 1.5  * 1.2
#     editor.spawn_static_mesh(SpawnableMeshes(cname), location = (-5.000 + x,0.150 + y, 0.3), scale=2, adjust_z=True)
#     i += 1



        
### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###
editor.set_goals_intro_text(f"Use a deep learning approach to sum up the value of all coins on the green slab. Enter the result in the InputBox. Do this {NUM_RUNS} times. While you should avoid false predictions, you can skip a set of coins by spawning in the next set.")
editor.specify_goal("acc_goal", "Do not make any false predictions", None, 0, is_optional=True)
editor.specify_goal("coin_result", "What is the sum of the coins \(in Euro cents\)?", None, 1)

### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the "AI Ass" chat in-game. ###
editor.add_hint(0,["What is the other camera for?","What are the coins on the purple slab for?", "How can I get reference images for all coins?"], "The coins on the purple slab are for training and their correct sum is available in the DataExchange under key 'train_sum'. Use the camera called 'reference_cam' to get the corresponding image. Now train a deep learning model that tries to map the image to the coin sum value.")
### END HINTS ###


### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###
def on_input(box:InputBox,gt:float,txt:str):
    val = -1.0
    if txt != "":
        try:
            val = float(txt)
            assert(val>=0)
        except:
            print(f"{txt} is not a valid number > 0", col=Colors.Red)
            return
    if abs(data.sum - val) < 1.01:
        data.num_correct += 1
        prog = data.num_correct / NUM_RUNS
        editor.set_goal_progress("coin_result", prog, f"What is the sum of the coins \(in Euro cents\)? {data.num_correct} / {NUM_RUNS}")
        if data.num_incorrect == 0:
            editor.set_goal_state("acc_goal", GoalState.Success) 
        if prog < 1:
            data.spawn_next()
        return
    if txt.strip() != "":
        print(f"{txt} is not correct...", col=Colors.Red)
        data.num_incorrect += 1
        editor.set_goal_state("acc_goal", GoalState.Fail)  

    
        

def begin_play():
    print("begin play")
    InputBox.find("coin_result").on_changed(on_input)
    on_reset()

editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    print("level resetting")
    for cam in SmartCamera.find_all():
        cam.set_fov(52)
    data.reset()
    data.spawn_next()
    
    inp = InputBox.find("coin_result")
    inp.set_text("")
    inp.editor_set_hint_text(f"Enter coin sum...")
    editor.set_goal_progress("coin_result", 0.0)
    editor.set_goal_progress("acc_goal", 0.0)
    editor.set_goal_state("acc_goal", GoalState.Open, "Do not make any false predictions.")  


editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###
def on_player_command(gametime:float, entity_type:str, entity_name:str, command:str, val:NPArray):
    #print(f"{entity_type=}, {entity_name=}, {command=}")
    if entity_name == "train_spawn" and command == "Spawn":
        data.spawn_next()

editor.on_player_command(on_player_command)

# ### ON PLAYER COMMAND CODE - Add code that shoule be executed each time the player issues a code command to an entity
# def on_player_command(gametime:float, entity_type:str, entity_name:str, command:str, val:NPArray):
#     if command == "setData":
#         data.predict_count += 1

# editor.on_player_command(on_player_command)
# ### END ON PLAYER COMMAND CODE ###

# ### LEVEL TICK CODE - Add code that should be executed on every simulation tick. ###
# def on_tick(simtime: float, deltatime: float):
#     pass

# editor.on_tick(on_tick)
# ### END LEVEL TICK CODE ###


### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###
