from panda_collisions import panda_collisions#CollisionWrapper

from direct.gui.DirectGui import DirectFrame
from direct.showbase import ShowBase

from vector import vector

class Ball:
    def __init__(self):
        self.speed_vector = vector.Vector(0,0,0)
        self.position = vector.Vector(0,0,0.9)
        

class Flipper:
    def __init__(self):
        self.score = 0
        self.balls_remaining = 3
        
        
        self.current_ball = Ball()
        frame_size = (-0.05,0.05,-0.05,0.05)
        pos = (0,0,0.9)
        self.current_ball.F = DirectFrame(pos=pos,frameSize=frame_size)
        self.gravity = vector.Vector(0,0,-0.0001)
        
        pos=(-0.5,0,-0.5)
        frame_size=(0,0.4,-0.05,0.0)
        self.left_bar = DirectFrame(pos=pos,frameSize=frame_size)
        self.left_deg = 0
        
        pos=(0.5,0,-0.5)
        frame_size=(0,-0.4,-0.05,0.0)
        self.right_bar = DirectFrame(pos=pos,frameSize=frame_size)
        self.right_deg = 0
        
    def main(self):
        if self.current_ball!=None:
            self.current_ball.speed_vector += self.gravity
            self.current_ball.position += self.current_ball.speed_vector
            self.current_ball.F.setPos(*self.current_ball.position)
            
            if self.current_ball.position[2] < -0.9:
                print("you lost!")
                self.current_ball.F.removeNode()
                self.current_ball = None
        
        self.left_deg-=1
        self.left_bar.setHpr(0,0,self.left_deg)
        
        self.right_deg+=1
        self.right_bar.setHpr(0,0,self.right_deg)
        
class Wrapper:
    def __init__(self):
        self.b = ShowBase.ShowBase()

def main():
    W = Wrapper()
    W.flipper=Flipper()
    
    while True:
            
            #delta_t = globalClock.dt
            #inputs = W.outputs
        
        W.flipper.main()#delta_t,inputs)
        
        #    W.outputs=[]
            
        W.b.taskMgr.step()

if __name__ == "__main__":
    main()
