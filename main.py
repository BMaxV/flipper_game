from panda_collisions import panda_collisions  # CollisionWrapper

from direct.showbase import DirectObject # event handler
from direct.gui.DirectGui import DirectFrame # 2d UI
from direct.showbase import ShowBase # window

from vector import vector

import math

# remember that writing this script took me the productive part of two
# whole days.

# even if you adapt things, and even if you copy paste,
# dealing with this, understanding this, will take time.
# don't be hard on yourself for not immediately getting it,
# but also keep in mind that this "figuring it out" is literally 99% of
# the time spent. You have to enjoy fiddling with it, if it's to be 
# your long time hobby.


class WorldObject:
    def __init__(self,id):
        self.id = id
        self.verts = []
        self.faces = [[0,1,2,3]] # this has to be a list of lists, with
        # one entry. best don't change this if you don't want to 
        # dig into how object creation works.
                

class Ball:
    def __init__(self,position=(0,0,0.9)):
        self.speed_vector = vector.Vector(0, 0, 0)
        self.position = vector.Vector(*position)

class Flipper:
    def __init__(self):
        self.score = 0
        self.balls_remaining = 3
        self.current_ball = None
        self.output_for_physics = {}
        self.past_collisions = []
        
        # so, I'm doing things in 2d with 2d UI frames,
        # because I didn't want to make 3d objects for this.
        
        # the perpective is top down.
        
        # the collision is still done in 3d, but I'm restricting 
        # movement to 2d. but I still need some 3d info.        
        
        # DirectFrame is just a 2d square or rectangle that SHOWS
        # the state. 
        
        # WorldObjects hold the 3d information for the walls and flippers.
        self.gravity = vector.Vector(0, 0, -0.0001)

        pos = (-0.5, 0, -0.5)
        frame_size = (0, 0.4, -0.05, 0.0)
        self.left_bar = DirectFrame(pos=pos, frameSize=frame_size)
        self.left_deg = 0
        self.left_bar_WO = WorldObject("7")
        
        # ... because of more panda shenanigans, this -1 and 1
        # are the z position for the walls THAT YOU CANT SEE
        # because we're looking top down.
        self.left_bar_WO.verts = [(0,-1,0),(0.4,-1,0),(0.4,1,0),(0,1,0)]
        self.left_bar_WO.pos = pos

        pos = (0.5, 0, -0.5)
        
        # 0.05 is the thickness of the bar
        frame_size = (0, -0.4, -0.05, 0.0) 
        self.right_bar = DirectFrame(pos=pos, frameSize=frame_size)
        self.right_deg = 0
        self.right_bar_WO = WorldObject("8")
        # otherwise the verts copy the size of the bar, from 0 to -0.4
        self.right_bar_WO.verts = [(0,-1,0),(-0.4,-1,0),(-0.4,1,0),(0,1,0)]
        self.right_bar_WO.pos = pos
                
        self.make_environment()
        
        # this is colliding with something, but it's fetching
        # the wrong id?
        
        self.env_phys_init_dict["create complex"].update({
                            "7":[self.left_bar_WO,"wall"],
                            "8":[self.right_bar_WO,"wall"],
                            })
        
    
    def make_new_ball(self):
        pos = (-0.2, 0, -0.1)
        self.current_ball = Ball(position=pos)
        frame_size = (-0.05, 0.05, -0.05, 0.05)
        
        # because of panda shenanigans, this 0.9 is the relative y position
        # on the screen. It means "center, almost at the top"
        
        self.current_ball.F = DirectFrame(pos=pos, frameSize=frame_size)
        
    def make_environment(self):
        
        #top
        pos = (0, 0, 0.95)
        frame_size = (-0.9, 0.9, -0.05, 0.0)
        F = DirectFrame(pos=pos, frameSize=frame_size)
        top_wo = WorldObject("4")
        top_wo.verts = [(-1,1,0),
                        (-1,-1,0),
                        (1,-1,0),
                        (1,1,0)]
        top_wo.pos = pos
        
        #left
        pos = (-0.9, 0, 0)
        frame_size = (-0.0, 0.05, -0.8, 0.9)
        F = DirectFrame(pos=pos, frameSize=frame_size)
        left_wo = WorldObject("5")
        left_wo.verts = [(0,-1,-1),
                        (0,1,-1),
                        (0,1,1),
                        (0,-1,1)]
        left_wo.pos = pos
        
        #right
        pos = (0.9, 0, 0)
        frame_size = (-0.05, 0.0, -0.8, 0.9)
        F = DirectFrame(pos=pos, frameSize=frame_size)
        right_wo = WorldObject("6")
        right_wo.verts = [(0,-1,-1),
                        (0,1,-1),
                        (0,1,1),
                        (0,-1,1)]
        right_wo.pos = pos
        
        #bumper1
        bumper1_pos = (-0.2, 0, 0)
        frame_size = (-0.05, 0.05, -0.05, 0.05)
        F = DirectFrame(pos=bumper1_pos, frameSize=frame_size)
        
        #bumper2
        bumper2_pos = (0.12, 0, 0.2)
        frame_size = (-0.05, 0.05, -0.05, 0.05)
        F = DirectFrame(pos=bumper2_pos, frameSize=frame_size)
        
        # ok this is the first dict.
        self.env_phys_init_dict={}
                            
        self.env_phys_init_dict.update({"create complex":{
                            "4":[top_wo,"NPC",],
                            "5":[left_wo,"NPC"],
                            "6":[right_wo,"NPC"],
                            },})
        
        self.env_phys_init_dict.update({"update":{
                            "2":(bumper1_pos,None),
                            "3":(bumper2_pos,None),
                            },})


    def main(self,inputs,collisions):
        phys_update_dict = {"update":{}}
        
        if self.current_ball != None:
            self.current_ball.speed_vector += self.gravity
            self.current_ball.position += self.current_ball.speed_vector
            self.current_ball.position.y = 0 #2d, ball is on a 2d surface.
            # collision can introduce a 3d component we don't want.
            
            self.current_ball.F.setPos(*self.current_ball.position)

            if self.current_ball.position[2] < -0.9:
                print("you lost!")
                self.current_ball.F.removeNode()
                self.current_ball = None
                
        bar_speed = 5
        if "left bar" in inputs and self.left_deg < 30:
            self.left_deg += bar_speed
            self.left_bar.setHpr(0, 0, -self.left_deg)
            
        elif self.left_deg > -30 and "left bar" not in inputs:
            self.left_deg -= bar_speed
            self.left_bar.setHpr(0, 0, -self.left_deg)
        
        if "right bar" in inputs and self.right_deg < 30:
            self.right_deg += bar_speed
            self.right_bar.setHpr(0, 0, self.right_deg)
            
        elif self.right_deg > -30 and "right bar" not in inputs:
            self.right_deg -= bar_speed
            self.right_bar.setHpr(0, 0, self.right_deg)
        
        phys_update_dict["update"]["7"]=(self.left_bar_WO.pos,(0, 0, -self.left_deg))
        phys_update_dict["update"]["8"]=(self.right_bar_WO.pos,(0, 0, self.right_deg))
        
        if "1" in collisions:
            for x in collisions["1"]:
                if x in self.past_collisions:
                    continue
                print("col",collisions["1"][x])
                # this is probably causing problems, because 
                # I switched y and z.
                
                col_v = collisions["1"][x]["collision normal"]
                col_v = vector.Vector(*col_v)
                # that's not how reflections work.
                # reflections work by mirroring the movementvector
                # along the normal of the thing.
                
                # this adds the angular velocity of the flipper
                # bar to the reflected movement, along the normal
                # of the reflection... uh.
                bar_speed_increase = 0
                #add the appropriate angular velocity of the bar
                if x == "7":
                    d = self.current_ball.position - self.right_bar_WO.pos
                    bar_speed_increase = d.magnitude()/0.4 * math.sin(bar_speed/360)
                    
                if x == "8":
                    d = self.current_ball.position - self.right_bar_WO.pos
                    
                    bar_speed_increase = d.magnitude()/0.4 * math.sin(bar_speed/360)
                    
                reflected_movement = reflection(self.current_ball.speed_vector,col_v)
                m = reflected_movement.magnitude()
                
                frac = (bar_speed_increase/m)
                print(bar_speed_increase)
                print("frac",frac)
                
                self.current_ball.speed_vector = reflected_movement+col_v*bar_speed_increase
                
                # add it to past bounces, so I don't bounce back and
                # forth in the same spot.
                self.past_collisions.append(x)
            
        rml=[]
        for x in self.past_collisions:
            if collisions!={}:
                if x not in collisions["1"]:
                    rml.append(x)
            else:
                rml.append(x)
                
        for x in rml:
            self.past_collisions.remove(x)
            print("removed",x)
         # update the status.
         
        if self.current_ball != None:            
            phys_update_dict["update"].update({"1":(self.current_ball.position,None)})
        
        if "new ball" in inputs and self.current_ball==None:
            # do something, also create a new physics ball.
            self.make_new_ball()
            phys_update_dict["create"] = {1:"NPC"}
        
        return phys_update_dict

def test_reflection():
    
    v1 = vector.Vector(0,0,-1)
    v2 = vector.Vector(0.05,0,1)
    v2 = v2.normalize()
    r = reflection(v1,v2)
    r = r.normalize()
    print(r)
    
    v1 = vector.Vector(0,0,-1)
    v2 = vector.Vector(-0.05,0,1)
    v2 = v2.normalize()
    r = reflection(v1,v2)
    r = r.normalize()
    print(r)
    
    v1 = vector.Vector(1,0,-1)
    v2 = vector.Vector(0,0,1)
    r = reflection(v1,v2)
    print(r)
    
    v1 = vector.Vector(1,0,-1)
    v2 = vector.Vector(1,0,0)
    r = reflection(v1,v2)
    print(r)
    
    v1 = vector.Vector(1,0,0)
    v2 = vector.Vector(1,0,1)
    r = reflection(v1,v2)
    print(r)

def reflection(speed_vector,collision_normal):
    """
        
    """
    col_vec=collision_normal.normalize()
    
    rotM = vector.RotationMatrix(math.pi, col_vec)
    new_speed_vector = -1*(rotM * speed_vector)
    return new_speed_vector

def move_task(*args):
    """
    see wrapper create move task
    """
    
    Task = args[1]
    wrapper = args[0]
    
    is_down = wrapper.b.mouseWatcherNode.is_button_down
    
    for mb in wrapper.buttons_move_actions:
        if is_down(mb):
            wrapper.pass_on(wrapper.buttons_move_actions[mb])
    
    return Task.cont


class Wrapper:
    def __init__(self):
        
        # separating these is intentional.
        # you don't need a graphical window to calculate collisionss
        # you don't need game rules to calculate collisions.
        
        # panda_stuff to get a window
        self.b = ShowBase.ShowBase()
        
        # for accepting inputs
        self.inputs=[]
        self.event_handler = DirectObject.DirectObject()
        self.event_handler.accept("y",self.pass_on,["left bar"])
        self.event_handler.accept("m",self.pass_on,["right bar"])
        self.event_handler.accept("l",self.pass_on,["new ball"])
        
        # game rules and data
        self.flipper = Flipper()
        
        # collisions
        self.collisions = panda_collisions.CollisionWrapper()
        
        # this creates the physics objects for the environemnt.
        # still need to create one for the ball every time I create a new
        # ball.
        
        
        self.collisions.create_collision_node("2","NPC",radius=0.15)
        self.collisions.create_collision_node("3","NPC",radius=0.15)
        
        print("YO")
        print(self.flipper.env_phys_init_dict)
        self.collisions.update(self.flipper.env_phys_init_dict)
        
        print(self.collisions.collision_objects)
        
        self.buttons_move_actions = {"y":"left bar","m":"right bar","l":"new ball"}
        self.create_move_task()
    
    def create_move_task(self):
        """annoying piece of panda cruft, can't track continuous input/
        held buttons without this."""
        print("move task created")
        self.b.taskMgr.add(move_task,"Move Task",extraArgs=[self],appendTask=True)
    
    def pass_on(self,stuff,*args):
        """
        just shove inputs into a list when the key is pressed
        fetch it when I want to in the main loop
        """
        if stuff not in self.inputs:
            self.inputs.append(stuff)


def main():
    W = Wrapper()
    
    while True:
        collision_data = W.collisions.collision_checks() # collisions
        update_data = W.flipper.main(W.inputs,collision_data)  # game logic
        W.inputs = []
        
        if "create" in update_data:
            W.collisions.create_collision_node("1","NPC",radius=0.03)
            update_data.pop("create")        
        
        W.collisions.update(update_data) # update collision state from game state
        W.b.taskMgr.step() # this renders and does the hardware/inputs

if __name__ == "__main__":
    main()
    #test_reflection()
