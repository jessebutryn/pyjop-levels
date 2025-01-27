### INIT CODE - DO NOT CHANGE ###
from pyjop import *

SimEnv.connect()
editor = LevelEditor.first()
### END INIT CODE ###

### IMPORTS - Add your imports here ###
import random
### END IMPORTS ###

### DATA MODEL - Define a data model needed for this custom level to share data between function calls ###
class DataModel(DataModelBase):
    def __init__(self) -> None:
        super().__init__()
        self.crossed_finish = False

data = DataModel()
### END DATA MODEL ###


### CONSTRUCTION CODE - Add all code to setup the level (select map, spawn entities) here ###
editor.select_map(SpawnableMaps.InfinitePlane)
editor.set_map_bounds((60,0,0), (140,20,16))
editor.spawn_entity(SpawnableEntities.HumanoidRobot, "runner", location=(5, 0, 0))
editor.spawn_entity(SpawnableEntities.TriggerZone, "finish", location=(115, 0, 0), scale = (1,5,2))
editor.spawn_entity(SpawnableEntities.SmartSpotLight, "finishlight", location=(115, 0, 3), rotation = (0,10,0))

def spawn_hurdles():
    for i in range(10):
        editor.spawn_static_mesh(SpawnableMeshes.SmallFence, location=(15 + 10*i, 0, 0), rotation=(0,0,90), is_temp=True)
### END CONSTRUCTION CODE ###


### GOAL CODE - Define all goals for the player here and implement the goal update functions. ###
def speedo_goal(goal_name: str):
    if data.crossed_finish:
        editor.set_goal_state(goal_name,GoalState.Success)
    else:
        editor.set_goal_state(goal_name,GoalState.Open)

editor.set_goals_intro_text("This is a 110m hurdle track. There is a hurdle every 10 meters.")
editor.specify_goal("speedo_goal", "Run the 110m hurdle track as fast as you can.", speedo_goal)
### END GOAL CODE ###


### HINTS CHAT - Define custom hints as question / answer pairs that the player can get answers to via the assistant chat in-game. Consecutive hints are hidden until the direct precursor is revealed.###
editor.add_hint(0,["How can I run?","How can I control the robot?"], """You can control the robot using the following snippet to make him move:
[#9CDCFE](robo) = [#4ABCA5](HumanoidRobot).[#DCDCAA](first)\(\)
[#9CDCFE](robo).[#DCDCAA](set_walking)\([#9CDCFE](yaw_angle) = [#B5CEA8](90), [#9CDCFE](speed)=[#B5CEA8](0.5)\)
""")

editor.add_hint(2,["How to make the robot jump?","How can I jump?"], """You can make the robot jump like this:
[#9CDCFE](robo) = [#4ABCA5](HumanoidRobot).[#DCDCAA](first)\(\)
[#9CDCFE](robo).[#DCDCAA](jump)\(\)
""")

### END HINTS ###


### ON BEGIN PLAY CODE - Add any code that should be executed after constructing the level once. ###
def on_finish_line(trigger:TriggerZone, gt:float, dat:TriggerEvent):
    if dat.entity_name == "runner" and not data.crossed_finish:
        data.crossed_finish = True
        light = SmartLight.find("finishlight")
        light.set_color(Colors.Green)
        editor.show_vfx(SpawnableVFX.Fireworks1, location = (125, 0, -5))
        
def begin_play():
    print("begin play")
    t = TriggerZone.first()
    t.on_triggered(on_finish_line)
    SmartLight.find("finishlight").set_color(Colors.Red)
    SmartLight.find("finishlight").set_intensity(50)
    # #add player placeable range finder
    # editor.set_building_budget(0)
    # editor.set_allowed_buildings([BuildingEntry(SpawnableEntities.RangeFinder,1)], True, True)
    on_reset()


editor.on_begin_play(begin_play)
### END ON BEGIN PLAY CODE ###


### ON LEVEL RESET CODE - Add code that should be executed on every level reset. ###
def on_reset():
    print("level resetting")
    data.reset()
    spawn_hurdles()


editor.on_level_reset(on_reset)
### END ON LEVEL RESET CODE ###



### EOF CODE - DO NOT CHANGE ###
editor.run_editor_level()
### EOF ###
