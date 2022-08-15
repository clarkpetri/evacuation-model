from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector
import math

def best_move(options, target):
    """
    Calculate best move based on Euclidian distance to exits
    """
    length_dict = {}
    
    for point in options:
        lst = []
        for t in target:
            lst.append(math.dist(point, t))
    
        short = min(lst)
        length_dict[point] = short

        
    temp = min(length_dict.values())
    res = [key for key in length_dict if length_dict[key] == temp]
    
    return res[0]

def agi_calc(self):
    """
    Calculate agitation total
    """
    agi_total = 0
    count = 0
    self.hero_present = False

    for agent in self.schedule.agents:
        if agent.type == "normal" and agent.pos in self.zone:
            count += 1
            agi_total += agent.agitation
            
            if agent.hero == True:
                self.hero_present = True

    return (agi_total, count, self.hero_present)


class EvacuationAgent(Agent):
    """
    Evacuation Agent
    """

    def __init__(self, pos, model, agent_type, exit, agitation, hero):
        """
        Create a new evacuation agent.
        """
        super().__init__(pos, model)
        self.pos = pos
        self.type = agent_type
        self.exit = exit
        self.agitation = agitation
        self.hero = hero 

    def step(self):

        if self.pos in self.exit:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
            self.model.escaped += 1

        else:

            if self.pos in self.model.zone:
                if self.agitation <= (1.0 - self.model.agi_gain):
                    self.agitation += self.model.agi_gain

            possible_steps = self.model.grid.get_neighborhood(self.pos,moore=True,include_center=False)
            empty_steps = []
            for step in possible_steps:
                if self.model.grid.is_cell_empty(step) == True:
                    empty_steps.append(step)

            if len(empty_steps):

                selection = best_move(empty_steps, self.exit)
                    
                if selection in self.exit:
                    self.model.grid.move_agent(self, selection)
                    self.model.grid.remove_agent(self)
                    self.model.schedule.remove(self)
                    self.model.escaped += 1

                else:
                    self.model.grid.move_agent(self, selection)


class MalevolentAgent(Agent):
    """
    Malevolent agent that doesn't escape but tries to reach exit area and impede escape
    """
    
    def __init__(self, pos, model, agent_type, exit):
        """
        Initialize the malevolent agent.
        """
        super().__init__(pos, model)
        self.pos = pos
        self.type = agent_type
        self.exit = exit

    def step(self):

        if self.pos in self.exit:

            self.exit.remove(self.pos)
            self.model.schedule.remove(self)

        else:
            possible_steps = self.model.grid.get_neighborhood(self.pos,moore=True,include_center=False)
            empty_steps = []
            for step in possible_steps:
                if self.model.grid.is_cell_empty(step) == True:
                    empty_steps.append(step)

            if len(empty_steps):
                
                selection = best_move(empty_steps, self.exit)
                self.model.grid.move_agent(self, selection)

class WallAgent(Agent):
    """
    Agent that acts as a wall. No interaction with other agents. Not added to schedule.
    """

    def __init__(self, pos, model, agent_type, wall):
        """
        Create a new wall agent.
        """
        super().__init__(pos, model)
        self.pos = pos
        self.type = agent_type
        self.wall = wall

    def step(self):

        None


class Evacuation(Model):
    """
    Evacuation model where good agents (blue) attempt to leave the space in the presence
    of malevolent agent(s) (red) that resist evacuation attempts
    """

    def __init__(self, width=20, height=20, seed=None, density=0.75, hero_prob = 0.05, malevolent=1, wall=None, engage=False, hero_present=False, exit=None, exit_bu=None, zone=None, tipping_point = 0.5, m_list=None, agi_gain=0.1):

        self.schedule = RandomActivation(self)
        self.grid = SingleGrid(width, height, torus=False)

        wall = [(0,0),(1,0),(2,0),(3,0),(4,0),(7,0),(8,0),(9,0),(10,0),(11,0),
            (12,0),(15,0),(16,0),(17,0),(18,0),(19,0),(0,1),(1,1),
            (2,1),(3,1),(4,1),(7,1),(8,1),(9,1),(10,1),(11,1),(12,1),
            (15,1),(16,1),(17,1),(18,1),(19,1),(8,11),(9,11),(10,11),(11,11),
            (8,10),(9,10),(10,10),(11,10),(8,9),(9,9),(10,9),(11,9),
            (8,8),(9,8),(10,8),(11,8)]

        escape = [(5,0),(6,0),(13,0),(14,0)]
        escape_bu = [(5,0),(6,0),(13,0),(14,0)]

        zone1 = self.grid.get_neighborhood((4,2),moore=True,include_center=True)
        zone2 = self.grid.get_neighborhood((7,2),moore=True,include_center=True)
        zone3 = self.grid.get_neighborhood((12,2),moore=True,include_center=True)
        zone4 = self.grid.get_neighborhood((15,2),moore=True,include_center=True)    
        zone = zone1 + zone2 + zone3 + zone4

        agitation = 0 

        self.width = width
        self.height = height
        self.seed = seed
        self.density = density
        self.hero_prob = hero_prob
        self.malevolent = malevolent
        self.wall = wall
        self.engage = engage
        self.hero_present = hero_present
        self.exit = escape
        self.exit_bu = escape_bu
        self.zone = zone
        self.tipping_point = tipping_point
        self.m_list = []
        self.agi_gain = agi_gain
        
        self.escaped = 0

        m_count = 0
        e_count = 0
        
        end = (len(wall) + self.malevolent)
            
        for pos in wall:
            agent_type = 'wall'
            agent = WallAgent(pos, self, agent_type, wall)
            self.grid.position_agent(agent, pos[0], pos[1])
            self.schedule.add(agent)

        for cell in self.grid.coord_iter():
            x = cell[1]
            y = cell[2]

            if (x,y) not in wall:
                if self.random.random() < self.density:

                    if m_count < malevolent:

                        agent_type = 'malevolent'
                        agent = MalevolentAgent((x, y), self, agent_type, escape)
                        self.grid.position_agent(agent, (x, y))
                        self.schedule.add(agent)
                        self.m_list.append(agent)
                        m_count += 1

                    else:

                        agent_type = 'normal'
                        if self.random.random() < self.hero_prob:
                            hero = True
                        else:
                            hero = False
                        agent = EvacuationAgent((x, y), self, agent_type, escape, agitation, hero)
                        self.grid.position_agent(agent, (x, y))
                        self.schedule.add(agent)
                        e_count += 1

        self.datacollector = DataCollector(
            {
            "Agents": lambda m: m.schedule.get_agent_count() - len(wall),
            "Agent Percent Remaining": lambda c: ((c.schedule.get_agent_count() - len(wall))/(e_count + m_count))*100,
            "Engage": lambda n: n.engage,
            })

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        """
        Run one step of the model. If All agents are have escaped, halt the model.
        """

        self.schedule.step()

        result = agi_calc(self)

        #print("Avg agitation:",result[0]/result[1])
        
        if len(self.exit) < 4:
            if result[1] > 0:
                if result[0]/result[1] > self.tipping_point:
                    if result[2] == True:
                        self.engage = True

        if self.engage == True:
            None

        #print("Exit:",self.exit)
        #print("Exit BU:",self.exit_bu)
        delta = [x for x in self.exit_bu if x not in self.exit]
        #print("Delta:",delta)
        #print("M_list:",self.m_list)
        if self.engage == True:
            
            for a in self.m_list:

                if a.pos in delta:
                    self.exit.append(a.pos)
                    self.grid.remove_agent(a)
                    
                    #print("New self.exit:",self.exit)
                    self.m_list.remove(a)


        # collect data
        self.datacollector.collect(self)

        if self.schedule.get_agent_count() == len(self.wall): # Stops model when only wall agents remain (doesn't need to count malevolent since they remove)   
            #print(self.schedule.get_agent_count())
            #print("Malevolent: ",self.malevolent)                          
            #print("Wall: ",len(self.wall))
            self.schedule.step()
            self.running = False