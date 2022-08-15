from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement
from mesa.visualization.UserParam import UserSettableParameter

from model import Evacuation


class AgentElement(TextElement):
    """
    Display a text count of how many agents have escape.
    """

    def __init__(self):
        pass

    def render(self, model):
        return ("Agents escaped: " + str(model.escaped),
        "   Engage: " + str(model.engage))

def escape_draw(agent):
    """
    Portrayal Method for canvas
    """
    if agent is None:
        return

    if agent.type == 'malevolent':
        portrayal = {"Shape": "circle", "r": 0.5, "Filled": "true", "Layer": 0}
        portrayal["Color"] = ["#FF0000", "#FF0000"]
        portrayal["stroke_color"] = "#000000"

    if agent.type == 'wall':
        portrayal = {"Shape": "rect", "w": 1.0, "h": 1.0, "Filled": "true", "Layer": 0}
        portrayal["Color"] = ["#000000", "#000000"]
        portrayal["stroke_color"] = "#000000"
        
    if agent.type == 'normal':
        if agent.hero == True:
            portrayal = {"Shape": "circle", "r": 0.5, "Filled": "true", "Layer": 0}
            portrayal["Color"] = ["#00CC00", "#00CC00"]
            portrayal["stroke_color"] = "#000000"
        else:
            portrayal = {"Shape": "circle", "r": 0.5, "Filled": "true", "Layer": 0}
            portrayal["Color"] = ["#3333FF", "#3333FF"]
            portrayal["stroke_color"] = "#000000"
    return portrayal


agent_element = AgentElement()
canvas_element = CanvasGrid(escape_draw, 20, 20, 500, 500)

# This draws the line graph
escape_chart = ChartModule([{"Label": "Agents", "Color": "Black"}])

model_params = {
    "height": 20,
    "width": 20,
    "density": UserSettableParameter("slider", "Agent density", 0.75, 0.1, 1.0, 0.1),
    "malevolent": UserSettableParameter("slider", "Malevolent Agents", 1, 0.00, 3.0, 1.0),
    "hero_prob": UserSettableParameter("slider", "Hero Probability", 0.025, 0.00, 0.5, 0.025),
    "tipping_point": UserSettableParameter("slider", "Tipping Point", 0.5, 0.0, 1.0, 0.2),
    "agi_gain": UserSettableParameter("slider", "Agitation Increase", 0.1, 0.0, 1.0, 0.1)
    }

server = ModularServer(
    Evacuation, [canvas_element, agent_element, escape_chart], "Evacuation", model_params)