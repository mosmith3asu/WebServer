import asyncio
# from pursuit_evasion.agents import PlayerRender,PartnerRender,EvaderRender
# from game_enviorment import WorldRender
# from settings import *
import numpy as np
import pywebcanvas as pwc
# import math
"""https://gitlab.com/imbev/pywebcanvas/-/tree/master/docs/examples/snake"""


################################################################
##############    SETTINGS    ##################################
################################################################
win_params = {}
win_params['unit_width'] = 7
win_params['unit_height'] = 7
win_params['resolution'] = 100
win_params["unit"] = win_params['resolution']
win_params["width"] = win_params['unit_width']*win_params['resolution']
win_params["height"] = win_params['unit_height']*win_params['resolution']
win_params["bg"] = 'black'
win_params["fg"] = 'white'
win_params['pen_color'] = 'lightcoral'
win_params['wall_color'] = 'black'
win_params['empty_color'] = 'white'


player_params = {}
player_params['unit_scale'] = 0.8
player_params['sz'] = player_params['unit_scale']*win_params["unit"]
player_params['vel'] = win_params["unit"]
player_params["actions"] = win_params["unit"] *np.array([[0,0],[0,1],[1,0],[0,-1],[-1,0]])
player_params['ego'] = {'start':[1,1], 'color':'blue','shape':'circle','scale':0.9}
player_params['partner'] = {'start':[5,3], 'color':'cornflowerblue','shape':'circle','scale':0.8}
player_params['evader'] = {'start':[5,5], 'color':'green','shape':'rect','scale':1}





#################################################
############# TEST CASES ########################
#################################################
def test_world1():
    w = -1
    p= -2
    _ = 0 # empty

    world = np.array([
        [w, w, w, w, w, w, w],
        [w, p, _, _, _, _, w],
        [w, _, w, p, w, _, w],
        [w, _, _, _, _, _, w],
        [w, _, w, p, w, _, w],
        [w, _, _, _, _, p, w],
        [w, w, w, w, w, w, w],
              ])
    return world

test_params = {}
test_params['world1'] = test_world1()


################################################################
############## WORLD AND PLAYER OBJECTS ########################
################################################################
class PlayerRender:
    def __init__(self, x_pos, y_pos, color='blue',shape='rect',scale=1):
        self.color = color
        self.Actions = player_params['actions']
        self.vel = player_params['vel']
        self.sz = player_params['sz']*scale
        self.x_off = int((win_params['unit'] -  self.sz) / 2)
        self.y_off = int((win_params['unit'] -  self.sz) / 2)

        self.x_pos, self.y_pos = x_pos, y_pos
        self.shape = shape

        self.rect = pwc.Rect(x=self.x_pos, y=self.y_pos, color=self.color, width=self.sz, height=self.sz)
        # if self.shape == 'rect':
        #     self.rect = pwc.Rect(x=self.x_pos, y=self.y_pos,color=self.color, width=self.sz, height=self.sz)
        # else: # circle
        #     rad = self.sz
        #     self.circ = pwc.arc(self.x_pos, self.y_pos,rad,0,2*3.14,False)


    def move(self,action):
        if  isinstance(action,int) : action = self.Actions[action] # check if action is index
        if  max(np.abs(action))==1: action *= self.vel # check if is scaled to pixels
        self.x_pos += action[0] # Move X
        self.y_pos += action[1] # Move Y

    def draw(self):
        self.rect.x = self.x_pos * win_params["unit"] + self.x_off
        self.rect.y = (self.y_pos * win_params["unit"] + self.y_off)  # - self.rect.height
        self.rect.color = self.color
        canvas.render(self.rect)
        # if self.shape == 'rect':
        #     self.rect.x = self.x_pos * win_params["unit"] + self.x_off
        #     self.rect.y = (self.y_pos * win_params["unit"] +self.y_off) #- self.rect.height
        #     self.rect.color = self.color
        #     canvas.render(self.rect)
        # else: # circle
        #     self.circ.x = self.x_pos * win_params["unit"] + self.x_off
        #     self.circ.y = (self.y_pos * win_params["unit"] + self.y_off)  # - self.rect.height
        #     self.circ.color = self.color
        #     canvas.render(self.circ)



class WorldRender():
    def __init__(self,world_array, empty_val=0, wall_val = -1, pen_val = -2):
        self.world = world_array
        self.sColor = {}
        self.sColor[pen_val] = win_params['pen_color']
        self.sColor[wall_val] = win_params['wall_color']
        self.sColor[empty_val] = win_params['empty_color']

        self.w_scale = win_params['unit']
        self.h_scale = win_params['unit']

        self.sID = {}
        self.sID["pen"] = pen_val
        self.sID["wall"] = wall_val
        self.sID["empty"] = empty_val

        self.Rects = []


    def draw(self):
        nrows,ncols = np.shape(self.world)
        for r in range(nrows):
            for c in range(ncols):
                val = self.world[c,r]
                if not (val==self.sID["wall"]): # optional but reduces draws and uses background
                    color = self.sColor[val]
                    rect = pwc.Rect(x=r*self.h_scale,
                                    y=c*self.w_scale,
                                    width=(self.w_scale),
                                    height=(self.h_scale),
                                    color=color)
                    canvas.render(rect)
                    self.Rects.append(rect)


################################################################
####################### INITIALIZE OBJECTS #####################
################################################################
state = 1
x1,y1 =player_params['ego']['start']
x2,y2 =player_params['partner']['start']
x3,y3 =player_params['evader']['start']
ego     = PlayerRender(x1, y1, color=player_params['ego']['color'],shape=player_params['ego']['shape'],scale=player_params['ego']['scale'])
partner = PlayerRender(x2, y2, color=player_params['partner']['color'],shape=player_params['partner']['shape'],scale=player_params['partner']['scale'])
evader  = PlayerRender(x3, y3, color=player_params['evader']['color'],shape=player_params['evader']['shape'],scale=player_params['evader']['scale'])
world   = WorldRender(test_params['world1'])
canvas = pwc.Canvas(width=win_params["width"], height=win_params["height"])
canvas.background.fill(color=win_params["bg"] )


################################################################
############## INTERFACE COMMANDS OBJECTS ######################
################################################################
async def delay():
    if not state == 1:
        return
    await asyncio.sleep(0.25)

async def on_refresh():
    global state
    global world
    global ego
    global partner
    global evader

    canvas.clear()
    if state == 1:
        world.draw()
        evader.draw()
        ego.draw()
        partner.draw()


def controls(e):
    global ego
    if not state == 1:  return
    if e.code == 'KeyW':   ego.move([0, -1]) # up
    elif e.code == 'KeyS': ego.move([0, 1]) # down
    elif e.code == 'KeyA': ego.move([-1, 0]) # left
    elif e.code == 'KeyD': ego.move([1, 0]) # right


pwc.add_event_handler("keydown", controls)
loop = pwc.Loop()
loop.add_task("delay", delay)
loop.add_task("one_refresh", on_refresh)
loop.run()

