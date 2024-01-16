from panda_collisions import panda_collisions  # CollisionWrapper

from direct.gui.DirectGui import OnscreenText
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
        
        #this is for administration of my objects.
        self.object_id_counter = 1
        self.world_objects = {}
        self.frame_objects = {}
        
        self.bar_speed = 5
        self.switch_states = {}
        
        self.held_inputs = []
        
        self.score = 0
        
        self.multiplier = 1
        self.base_multiplier = 1
        
        self.temp_modifiers = {}
        
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
        self.make_left_bar()
        self.make_right_bar()
    
        self.make_environment()
        
        # this is colliding with something, but it's fetching
        # the wrong id?
        self.bar_ids=[self.left_bar_WO.id,self.right_bar_WO.id]
        self.env_phys_init_dict["create complex"].update({
                            self.left_bar_WO.id:[self.left_bar_WO,"wall"],
                            self.right_bar_WO.id:[self.right_bar_WO,"wall"],
                            })
        self.build_text()
        
    def build_text(self):
        scale = 0.05
        pos=(-0.95,0.95,0)
        text="Score:1000"
        self.score_text=OnscreenText(text=text, 
                    scale=scale,
                    pos=pos,
                    fg=(1,1,1, 1),
                    shadow=(0,0,0,1),
                    align=0)
        
        pos=(-0.95,0.9,0)
        text="multiplier:1x"
        self.multiplier_text=OnscreenText(text=text, 
                    scale=scale,
                    pos=pos,
                    fg=(1,1,1, 1),
                    shadow=(0,0,0,1),
                    align=0)
        
        pos = (-0.95,0.85,0)
        text = "balls:3"
        self.balls_text=OnscreenText(text=text, 
                    scale=scale,
                    pos=pos,
                    fg=(1,1,1, 1),
                    shadow=(0,0,0,1),
                    align=0)
        
    def make_left_bar(self):
        this_id=self.generate_object_id()
        
        # WorldObjects hold the 3d information for the walls and flippers.
        self.gravity = vector.Vector(0, 0, -0.0001)

        pos = (-0.5, 0, -0.5)
        frame_size = (0, 0.4, -0.05, 0.0)
        self.left_bar = DirectFrame(pos=pos, frameSize=frame_size)
        self.left_deg = 0
        self.left_bar_WO = WorldObject(this_id)
        
        self.world_objects[this_id]=self.left_bar_WO
        self.frame_objects[this_id]=self.left_bar
        
        # ... because of more panda shenanigans, this -1 and 1
        # are the z position for the walls THAT YOU CANT SEE
        # because we're looking top down.
        self.left_bar_WO.verts = [(0,-1,0),(0.4,-1,0),(0.4,1,0),(0,1,0)]
        self.left_bar_WO.pos = pos
        
    def make_right_bar(self):
        pos = (0.5, 0, -0.5)
        this_id=self.generate_object_id()
        # 0.05 is the thickness of the bar
        frame_size = (0, -0.4, -0.05, 0.0) 
        self.right_bar = DirectFrame(pos=pos, frameSize=frame_size)
        self.right_deg = 0
        self.right_bar_WO = WorldObject(this_id)
        # otherwise the verts copy the size of the bar, from 0 to -0.4
        self.right_bar_WO.verts = [(-0.4,-1,0),(0,-1,0),(0,1,0),(-0.4,1,0)]
        self.right_bar_WO.pos = pos
        self.world_objects[this_id]=self.right_bar_WO
        self.frame_objects[this_id]=self.right_bar
    
    def add_three_bumper_switches(self,pos,vector,name):
        """
        todo: this still creates the default sized bumper.
        but I want it a lot smaller. ok that's done.
        
        now, for my next trick, I want to do a rogue like thing
        where I select the tables and then inside the tables
        I want to gather power ups.
        
        but not just points, I want active abilities for my balls.
        """
        creation_dict = {}
        upd = {}
        self.switch_to_wo_ids = {}
        self.switch_states[name] = {}
        c = 0
        while c < 3:
            fpos = pos + c/3*vector
            fpos = tuple(fpos)
            frame_size = (-0.05,0.05,-0.05,0.05)
            this_id = self.generate_object_id()
            frame = DirectFrame(pos=fpos, frameSize=frame_size)
            #guard_left_WO = WorldObject(this_id)
            self.frame_objects[this_id] = frame
            frame.setColor(1,0,0)
            self.switch_to_wo_ids[this_id] = (name,c)
            self.switch_states[name][c] = False
            
            
            # this puts an entry to create a new default collision object
            creation_dict[this_id] = "NPC"
            # this puts the position and rotation data into the update
            # inputs for the collision system, so that the collision
            # object is in the same place as the graphical representation.
            upd.update({this_id:(fpos,(0,0,0))})
            c += 1
            
        return creation_dict, upd
        
    
    def generate_object_id(self):
        self.object_id_counter += 1
        return str(self.object_id_counter)
    
    def make_new_ball(self):
        pos = (-0.2, 0, -0.1)
        self.current_ball = Ball(position=pos)
        frame_size = (-0.05, 0.05, -0.05, 0.05)
        
        # because of panda shenanigans, this 0.9 is the relative y position
        # on the screen. It means "center, almost at the top"
        
        self.current_ball.F = DirectFrame(pos=pos, frameSize=frame_size)
        
    def make_environment(self):
        
        #top
        this_id=self.generate_object_id()
        pos = (0, 0, 0.95)
        frame_size = (-0.9, 0.9, -0.05, 0.0)
        F = DirectFrame(pos=pos, frameSize=frame_size)
        top_wo = WorldObject(this_id)
        top_wo.verts = [(-1,-1,0),
                        (-1,1,0),
                        (1,1,0),
                        (1,-1,0)]
        top_wo.pos = pos
        
        #left
        this_id=self.generate_object_id()
        pos = (-0.9, 0, 0)
        frame_size = (-0.0, 0.05, -0.8, 0.9)
        F = DirectFrame(pos=pos, frameSize=frame_size)
        left_wo = WorldObject(this_id)
        left_wo.verts = [(0,-1,-1),
                        (0,1,-1),
                        (0,1,1),
                        (0,-1,1)]
        left_wo.pos = pos
        
        #right
        this_id=self.generate_object_id()
        pos = (0.9, 0, 0)
        frame_size = (-0.05, 0.0, -0.8, 0.9)
        F = DirectFrame(pos=pos, frameSize=frame_size)
        right_wo = WorldObject(this_id)
        right_wo.verts = [(0,-1,1),
                        (0,1,1),
                        (0,1,-1),
                        (0,-1,-1),]
        right_wo.pos = pos
        
        #guard_right
        this_id = self.generate_object_id()
        pos = (0.9, 0, -0.25)
        frame_size = (-0.45, 0.0, -0.05, 0.00)
        guard_right = DirectFrame(pos=pos, frameSize=frame_size)
        guard_right_WO = WorldObject(this_id)
        guard_right_WO.verts = [
                        (-0.45,-1,0),
                        (0,-1,0),
                        (0,1,0),
                        (-0.45,1,0),                        
                        ]
        guard_right.setHpr(0,0,-30)
        guard_right_WO.pos = pos
        self.frame_objects[this_id] = guard_right
        self.world_objects[this_id] = guard_right_WO
        
        #guard_left
        this_id = self.generate_object_id()
        pos = (-0.9, 0, -0.25)
        frame_size = (0.0, 0.45, -0.05, 0.00)
        guard_left = DirectFrame(pos=pos, frameSize=frame_size)
        guard_left_WO = WorldObject(this_id)
        guard_left_WO.verts = [
                        (0.45,-1,0),
                        (0.45,1,0),
                        (0,1,0),
                        (0,-1,0)]
        
        guard_left.setHpr(0,0,30)
        guard_left_WO.pos = pos
        self.frame_objects[this_id] = guard_left
        self.world_objects[this_id] = guard_left_WO
        
        # ok this is the first dict.
        self.env_phys_init_dict={}
        
        self.env_phys_init_dict.update({"create complex":{
                            top_wo.id:[top_wo,"NPC",],
                            left_wo.id:[left_wo,"NPC"],
                            right_wo.id:[right_wo,"NPC"],
                            guard_right_WO.id:[guard_right_WO,"NPC"],
                            guard_left_WO.id:[guard_left_WO,"NPC"],
                            },})
        p = vector.Vector(-0.6,0,0.4)
        v = vector.Vector(1.2,0,0.2)
        my_d,upd = self.add_three_bumper_switches(p,v,"test")
        
        self.bumper_creation = my_d
        self.bumper_positions = upd
        
        self.env_phys_init_dict.update({"update":{
                    guard_right_WO.id:[guard_right_WO.pos,(0,0,-30)],
                    guard_left_WO.id:[guard_left_WO.pos,(0,0,30)],
                    }})
        
        self.env_phys_init_dict["update"].update(upd)
        
    def bar_activation(self,inputs):
        bar_speed = self.bar_speed
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
        

    def switch_rotation(self,inputs):
        if "left bar" in inputs and "left bar" not in self.held_inputs:
            var = "up"
        elif "right bar" in inputs and "right bar" not in self.held_inputs:
            var = "down"
        else:
            return
        
        # I could put this into a dedicated object...
        for name in self.switch_states:
            d = self.switch_states[name]
            numbers = d.keys()
            if var=="down":
                new_d = {0:d[2],
                        1:d[0],
                        2:d[1]}
            else:
                new_d = {0:d[1],
                        1:d[2],
                        2:d[0]}
            self.switch_states[name] = new_d
        self.recolor_switches()
        
    def recolor_switches(self):
        for x in self.frame_objects:
            if x in self.switch_to_wo_ids:
                name,c=self.switch_to_wo_ids[x]
                if self.switch_states[name][c]:
                    self.frame_objects[x].setColor(0,1,0)
                else:
                    self.frame_objects[x].setColor(1,0,0)
    
    
    def check_switch(self,x):
        """
        check if the collided object is a switch
        """
        if x in self.switch_to_wo_ids:
            self.score += 100*self.multiplier
            self.score_text.setText(f"Score:{self.score}")
            
            name,c = self.switch_to_wo_ids[x]
            self.switch_states[name][c] = not self.switch_states[name][c]
            if self.switch_states[name][c]:
                self.frame_objects[x].setColor(0,1,0)
            else:
                self.frame_objects[x].setColor(1,0,0)
            
            # check if the whole group is turned on!
            self.check_switch_group(name)
    
    def check_switch_group(self,name):
        """
        check if all switches of the group are "on"
        """
        all_p = True
        for x in self.switch_states[name]:
            if self.switch_states[name][x]==False:
                all_p = False
                return
        
        if all_p:
            self.multiplier += 1
            self.score += 200 * self.multiplier
            self.multiplier_text.setText(f"multiplier:{self.multiplier}x")
            # optionally append this to some multiplier list that
            # ticks down.
            print(name," group activated")
        
        for x in self.switch_states[name]:
            self.switch_states[name][x]=False
        
        self.recolor_switches()

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
                
        self.switch_rotation(inputs)
        
        self.bar_activation(inputs)
        
        # update bar rotation
        phys_update_dict["update"][self.bar_ids[0]]=(self.world_objects[self.bar_ids[0]].pos,(0, 0, -self.left_deg))
        phys_update_dict["update"][self.bar_ids[1]]=(self.world_objects[self.bar_ids[1]].pos,(0, 0, self.right_deg))
        
        
        if "1" in collisions:
            for x in collisions["1"]:
                if x in self.past_collisions:
                    continue
                
                # this is probably causing problems, because 
                # I switched y and z.
                self.check_switch(x)
            
                col_v = collisions["1"][x]["collision normal"]
                col_v = vector.Vector(*col_v)
                
                v_v = vector.Vector(*self.current_ball.speed_vector)
                v_v = v_v.normalize()
                
                ang2 = v_v.angle_to_other(col_v)
                
                if ang2 < math.pi/2:
                    
                    continue
                
                bar_speed = self.bar_speed
                bar_speed_increase = 0
                #add the appropriate angular velocity of the bar
                if x in self.bar_ids and ("left bar" in inputs or "right bar" in inputs):
                    d = self.current_ball.position - self.right_bar_WO.pos
                    bar_speed_increase = d.magnitude()/0.4 * math.sin(bar_speed/360)
                                        
                reflected_movement = reflection(self.current_ball.speed_vector,col_v)
                m = reflected_movement.magnitude()
                
                frac = (bar_speed_increase/m)
                                
                self.current_ball.speed_vector = reflected_movement+col_v*bar_speed_increase
                self.current_ball.speed_vector *= 0.9
                               
                # add it to past bounces, so I don't bounce back and
                # forth in the same spot.
                # it's not clear how I do rolling and "sling"
                # acceleration here...
                self.past_collisions.append(x)
        
        else:
            collisions = {}
        rml=[]
        for x in self.past_collisions:
            if collisions!={}:
                if x not in collisions["1"]:
                    rml.append(x)
            else:
                rml.append(x)
                
        for x in rml:
            self.past_collisions.remove(x)
            
         # update the status.
         
        if self.current_ball != None:            
            phys_update_dict["update"].update({"1":(self.current_ball.position,None)})
        
        if "new ball" in inputs and self.current_ball==None:
            # do something, also create a new physics ball.
            self.make_new_ball()
            phys_update_dict["create"] = {1:"NPC"}
        
        rml=[]
        for x in self.held_inputs:
            if x not in inputs:
                rml.append(x)
        for x in rml:
            self.held_inputs.remove(x)
        
        for x in inputs:
            if x not in self.held_inputs:
                self.held_inputs.append(x)
        
        
        
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
        l_button = "a"
        r_button = "l"
        n_button = "n"
        self.event_handler.accept(l_button,self.pass_on,["left bar"])
        self.event_handler.accept(r_button,self.pass_on,["right bar"])
        self.event_handler.accept(n_button,self.pass_on,["new ball"])
        self.buttons_move_actions = {l_button:"left bar",r_button:"right bar",n_button:"new ball"}
        self.create_move_task()
        
        # game rules and data
        self.flipper = Flipper()
        
        # collisions
        self.collisions = panda_collisions.CollisionWrapper()
        
        # this creates the physics objects for the environemnt.
        # still need to create one for the ball every time I create a new
        # ball.
        
        # this is a bit ugly... it would be more obvious if
        # I could create output from the init and parse that here.
        self.collisions.update(self.flipper.env_phys_init_dict)
        
        # these are some unfortunate hoops for non standard sized collision
        # things.
        for x in self.flipper.bumper_creation:
            tag = self.flipper.bumper_creation[x]
            self.collisions.create_collision_node(x,tag,0.05)
        
        # this is the regular update function, in this case used to
        # move the bumper collision objects to the correct position
        # but it's also used to update the ball position.
        self.collisions.update({"update":self.flipper.bumper_positions})
        
        for x in self.flipper.bumper_positions:
            ps = self.collisions.collision_objects[x].getPos()
        
    def create_move_task(self):
        """
        annoying piece of panda cruft, can't track continuous input/
        held buttons without this.
        """
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
