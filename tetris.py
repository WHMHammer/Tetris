from os import path,system
from platform import platform
from random import choice
from threading import Thread
from time import sleep

cls=lambda :system("cls" if "Windows" in platform() else "clear")

class Tetris:
    class __Block:
        def __init__(self,shape):
            self.shape=shape    #shape in "IJLOSTZ"
            self.ori=0    #orientation
            self.ref=[-1,3]    #point of reference
            self.rel={
                "I":(((1,0),(1,1),(1,2),(1,3)),((0,1),(1,1),(2,1),(3,1))),
                "J":(((1,0),(1,1),(1,2),(2,2)),((0,1),(1,1),(2,0),(2,1)),((0,0),(1,0),(1,1),(1,2)),((0,1),(0,2),(1,1),(2,1))),
                "L":(((1,0),(1,1),(1,2),(2,0)),((0,0),(0,1),(1,1),(2,1)),((0,2),(1,0),(1,1),(1,2)),((0,1),(1,1),(2,1),(2,2))),
                "O":(((1,1),(1,2),(2,1),(2,2)),),
                "S":(((1,2),(1,3),(2,1),(2,2)),((1,1),(2,1),(2,2),(3,2))),
                "T":(((1,0),(1,1),(1,2),(2,1)),((0,1),(1,0),(1,1),(2,1)),((0,1),(1,0),(1,1),(1,2)),((0,1),(1,1),(1,2),(2,1))),
                "Z":(((1,0),(1,1),(2,1),(2,2)),((1,2),(2,1),(2,2),(3,1)))
            }[self.shape]    #relative positions

    class __Autofall(Thread):
        def __init__(self,game):
            Thread.__init__(self)
            self.game=game
            self.start()

        def run(self):
            while self.game.isLegal():
                sleep(self.game.interval)
                self.game.down()
                self.game.display()

    def __init__(self):
        while True:
            cls()
            mode=input("Welcome to Tetris!\n\nW to rotate\nA to move left\nS to move down\nD to move right\nSpace to drop\nQ to quit\n\nNow, please select a mode: (E)asy, (M)edium, or (H)ard, or (Q)uit.\n")
            if mode=="":continue
            elif mode in "EeMmHh":
                self.interval,self.mode={"E":(2,0),"e":(2,0),"M":(1,1),"m":(1,1),"H":(0.5,2),"h":(0.5,2)}[mode]
                break
            elif mode in "Qq":exit()
        self.board=[]
        for i in range(20):
            self.board.append([])
            for j in range(10):self.board[i].append(" ")
        self.score=0
        self.isOver=False
        self.cur=self.__Block(choice("IJLOSTZ"))
        self.nxt=self.__Block(choice("IJLOSTZ"))
        self.guide()
        self.display()
        self.__Autofall(self)
        while self.isLegal():
            i=input()
            if i=="":pass
            elif i in "Qq":self.isOver=True
            else:{
                "W":self.rotate,
                "w":self.rotate,
                "A":self.left,
                "a":self.left,
                "S":self.down,
                "s":self.down,
                "D":self.right,
                "d":self.right,
                " ":self.drop
            }[i]()
            self.display()
        #Display the high scores:
        sleep(self.interval)
        with open(path.join(path.dirname(__file__),"tetrisHighScores.csv"),"r") as record:
            highScores=[]
            pos=10
            for i in range(10):
                highScores.append(record.readline()[:-1].split(","))
                highScores[i][0]=int(highScores[i][0])
                highScores[i][1]=int(highScores[i][1])
                if pos==10 and (self.score>highScores[i][0] or (self.score==highScores[i][0] and self.mode>highScores[i][1])):pos=i
        cls()
        if pos!=10:
            highScores.pop(-1)
            highScores.insert(pos,[self.score,self.mode,input("New high score!\nPlease type in your name:\n")])
            csv=""
            for i in range(10):
                csv+=str(highScores[i][0])+","+str(highScores[i][1])+","+highScores[i][2]+"\n"
            with open(path.join(path.dirname(__file__),"tetrisHighScores.csv"),"w") as record:
                record.write(csv)
            cls()
        print("High scores:")
        for i in range(10):
            print("*NEW*" if i==pos else "No.%2d"%(i+1),"%4d"%highScores[i][0],(" Easy ","Meidum"," Hard ")[highScores[i][1]],highScores[i][2])

    def display(self):
        cls()
        print("       T e t r i s")
        print(" --0-1-2-3-4-5-6-7-8-9--      - N E X T -")
        print(end=" 0|")
        for i in range(10):
            if (0-self.cur.ref[0],i-self.cur.ref[1]) in self.cur.rel[self.cur.ori]:print(self.cur.shape,end="|")
            elif (0,i) in self.shadow:print(end="*|")
            else:print(self.board[0][i],end="|")
        print(end="0      0|")
        for i in range(4):
            if (1,i) in self.nxt.rel[self.nxt.ori]:print(self.nxt.shape,end="|")
            else:print(end=" |")
        print("1")
        print(end=" 1|")
        for i in range(10):
            if (1-self.cur.ref[0],i-self.cur.ref[1]) in self.cur.rel[self.cur.ori]:print(self.cur.shape,end="|")
            elif (1,i) in self.shadow:print(end="*|")
            else:print(self.board[1][i],end="|")
        print(end="1      1|")
        for i in range(4):
            if (2,i) in self.nxt.rel[self.nxt.ori]:print(self.nxt.shape,end="|")
            else:print(end=" |")
        print("1")
        print(end=" 2|")
        for i in range(10):
            if (2-self.cur.ref[0],i-self.cur.ref[1]) in self.cur.rel[self.cur.ori]:print(self.cur.shape,end="|")
            elif (2,i) in self.shadow:print(end="*|")
            else:print(self.board[2][i],end="|")
        print("2      --3-4-5-6--")
        print(end=" 3|")
        for i in range(10):
            if (3-self.cur.ref[0],i-self.cur.ref[1]) in self.cur.rel[self.cur.ori]:print(self.cur.shape,end="|")
            elif (3,i) in self.shadow:print(end="*|")
            else:print(self.board[3][i],end="|")
        print("3")
        print(end=" 4|")
        for i in range(10):
            if (4-self.cur.ref[0],i-self.cur.ref[1]) in self.cur.rel[self.cur.ori]:print(self.cur.shape,end="|")
            elif (4,i) in self.shadow:print(end="*|")
            else:print(self.board[4][i],end="|")
        print("4      Score:",self.score,("(Easy)","(Medium)","(Hard)")[self.mode])
        for i in range(5,20):
            print("%2d"%(i),end="|")
            for j in range(10):
                if (i-self.cur.ref[0],j-self.cur.ref[1]) in self.cur.rel[self.cur.ori]:print(self.cur.shape,end="|")
                elif (i,j) in self.shadow:print(end="*|")
                else:print(self.board[i][j],end="|")
            print(str(i))
        print("  -0-1-2-3-4-5-6-7-8-9-")

    def rotate(self):
        ori=self.cur.ori
        self.cur.ori+=1
        if self.cur.ori==len(self.cur.rel):self.cur.ori=0
        if self.isLegal():self.guide()
        else:self.cur.ori=ori

    def left(self):
        self.cur.ref[1]-=1
        if self.isLegal():self.guide()
        else:self.cur.ref[1]+=1

    def down(self):
        self.cur.ref[0]+=1
        if not self.isLegal():
            self.cur.ref[0]-=1
            x,y=self.cur.ref
            for i in self.cur.rel[self.cur.ori]:
                self.board[x+i[0]][y+i[1]]=self.cur.shape
            for i in range(20):
                if " " not in self.board[i]:
                    self.board.pop(i)
                    self.board.insert(0,[" " for j in range(10)])
                    self.score+=1
            self.cur=self.nxt
            self.nxt=self.__Block(choice("IJLOSTZ"))
            self.guide()

    def right(self):
        self.cur.ref[1]+=1
        if self.isLegal():self.guide()
        else:self.cur.ref[1]-=1

    def drop(self):
        while self.cur.ref!=[-1,3]:self.down()

    def isLegal(self):
        if self.isOver:return False
        x,y=self.cur.ref
        for i in self.cur.rel[self.cur.ori]:
            if x+i[0] not in range(20) or y+i[1] not in range(10) or self.board[x+i[0]][y+i[1]]!=" ":return False
        return True

    def guide(self):
        rel=self.cur.rel[self.cur.ori]
        ref=self.cur.ref
        H=20
        for i in rel:
            x=ref[0]+i[0]
            y=ref[1]+i[1]
            for j in range(x+1,20):
                if self.board[j][y]!=" ":
                    h=j-x-1
                    break
            else:
                h=19-x
            if h<H:H=h
        self.shadow=[]
        for i in rel:self.shadow.append((i[0]+ref[0]+H,i[1]+ref[1]))

if __name__=="__main__":Tetris()