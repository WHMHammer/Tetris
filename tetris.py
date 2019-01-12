import sqlite3
from os import system
from os.path import abspath,dirname,join
from platform import platform
from random import choice
from threading import Thread
from time import sleep,time

cls=lambda :system("cls" if "Windows" in platform() else "clear")

class Block:
    def __init__(self,shape):
        self.shape=shape    #shape in "IJLOSTZ"
        self.ori=0    #orientation
        self.ref=[-1,3]    #point of reference
        self.rel={
            "I":(
                ((1,0),(1,1),(1,2),(1,3)),
                ((0,1),(1,1),(2,1),(3,1))
            ),
            "J":(
                ((1,0),(1,1),(1,2),(2,2)),
                ((0,1),(1,1),(2,0),(2,1)),
                ((0,0),(1,0),(1,1),(1,2)),
                ((0,1),(0,2),(1,1),(2,1))
            ),
            "L":(
                ((1,0),(1,1),(1,2),(2,0)),
                ((0,0),(0,1),(1,1),(2,1)),
                ((0,2),(1,0),(1,1),(1,2)),
                ((0,1),(1,1),(2,1),(2,2))
            ),
            "O":(
                ((1,1),(1,2),(2,1),(2,2)),
            ),
            "S":(
                ((1,2),(1,3),(2,1),(2,2)),
                ((1,1),(2,1),(2,2),(3,2))
            ),
            "T":(
                ((1,0),(1,1),(1,2),(2,1)),
                ((0,1),(1,0),(1,1),(2,1)),
                ((0,1),(1,0),(1,1),(1,2)),
                ((0,1),(1,1),(1,2),(2,1))
            ),
            "Z":(
                ((1,0),(1,1),(2,1),(2,2)),
                ((1,2),(2,1),(2,2),(3,1))
            )
        }[self.shape]    #relative positions

class Tetris:
    def __init__(self):
        while True:
            cls()
            mode=input("Welcome to Tetris!\n\nW to rotate\nA to move left\nS to move down\nD to move right\nSpace to drop\nP to pause\nQ to quit\n\nNow, please select a mode: (E)asy, (M)edium, or (H)ard, or (Q)uit.\n")
            try:
                self.interval,self.mode={
                    "e":(1,"Easy"),
                    "m":(0.5,"Medium"),
                    "h":(0.25,"Hard")
                }[mode]
            except KeyError:
                if mode=="q":
                    exit()
            else:
                break
        self.board=[]
        for i in range(20):
            self.board.append([])
            for j in range(10):self.board[i].append(" ")
        self.score=0
        self.quited=False
        self.cur=Block(choice("IJLOSTZ"))
        self.nxt=Block(choice("IJLOSTZ"))
        self.guide()
        self.display()
        self.autofall=Autofall(self)
        while self.islegal():
            i=input()
            if i=="":
                pass
            elif i=="q":
                self.quited=True
            elif i=="p":
                self.autofall.pause=True
                cls()
                print("Paused\n\nCurrent score:",self.score)
                input("\nPress ENTER to resume\n")
                self.autofall.pause=False
            else:
                try:
                    {
                        "w":self.rotate,
                        "a":self.left,
                        "s":self.down,
                        "d":self.right,
                        " ":self.drop
                    }[i]()
                except KeyError:
                    pass
            self.display()
        #Display the high scores:
        sleep(self.interval)
        conn=sqlite3.connect(join(dirname(abspath(__file__)),"tetris.db"))
        cur=conn.cursor()
        cur.execute("select * from %s order by score desc,time asc;"%self.mode)
        high_scores=cur.fetchall()
        i=0
        txt=""
        while i<10:
            record=high_scores[i]
            if self.score>record[1]:
                name=input("New high score!\nPlease type in your name:\n")
                txt+="*NEW*    %4d    %s"%(self.score,name)+"\n"
                cur.execute("delete from %s where time=?;"%self.mode,(high_scores[-1][0],))
                cur.execute("insert into %s values(?,?,?);"%self.mode,(int(time()),self.score,name))
                conn.commit()
                i+=1
                break
            txt+="No.%2d"%(i+1)+"    %4d    %s"%record[1:]+"\n"
            i+=1
        conn.close()
        cls()
        print("High Scores:")
        print(txt,end="")
        while i<10:
            print("No.%2d"%(i+1)+"    %4d    %s"%high_scores[i-1][1:])
            i+=1

    def display(self):
        cls()
        print("             T e t r i s")
        print(" --0-1-2-3-4-5-6-7-8-9--      - N E X T -")

        self.displayln(0)
        print("      0|%s|%s|%s|%s|0"%tuple(self.nxt.shape if (1,i) in self.nxt.rel[self.nxt.ori] else " " for i in range(4)))

        self.displayln(1)
        print("      1|%s|%s|%s|%s|1"%tuple(self.nxt.shape if (2,i) in self.nxt.rel[self.nxt.ori] else " " for i in range(4)))

        self.displayln(2)
        print("      --3-4-5-6--")

        self.displayln(3)
        print()

        self.displayln(4)
        print("      Score: %d (%s)"%(self.score,self.mode))

        for i in range(5,20):
            self.displayln(i)
            print()

        print("  -0-1-2-3-4-5-6-7-8-9-")

    def displayln(self,l):
        print(end="%2d|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%d"%((l,)+tuple(self.cur.shape if (l-self.cur.ref[0],i-self.cur.ref[1]) in self.cur.rel[self.cur.ori] else "*" if (l,i) in self.shadow else self.board[l][i] for i in range(10))+(l,)))

    def rotate(self):
        ori=self.cur.ori
        self.cur.ori+=1
        if self.cur.ori==len(self.cur.rel):
            self.cur.ori=0
        if self.islegal():
            self.guide()
        else:
            self.cur.ori=ori

    def left(self):
        self.cur.ref[1]-=1
        if self.islegal():
            self.guide()
        else:
            self.cur.ref[1]+=1

    def down(self):
        self.cur.ref[0]+=1
        if not self.islegal():
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
            self.nxt=Block(choice("IJLOSTZ"))
            self.guide()

    def right(self):
        self.cur.ref[1]+=1
        if self.islegal():
            self.guide()
        else:
            self.cur.ref[1]-=1

    def drop(self):
        while self.cur.ref!=[-1,3]:
            self.down()

    def islegal(self):
        if self.quited:
            return False
        x,y=self.cur.ref
        for i in self.cur.rel[self.cur.ori]:
            if x+i[0] not in range(20) or y+i[1] not in range(10) or self.board[x+i[0]][y+i[1]]!=" ":
                return False
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
            if h<H:
                H=h
        self.shadow=[]
        for i in rel:self.shadow.append((i[0]+ref[0]+H,i[1]+ref[1]))

class Autofall(Thread):
    def __init__(self,game):
        Thread.__init__(self)
        self.game=game
        self.pause=False
        self.start()

    def run(self):
        while self.game.islegal():
            sleep(self.game.interval)
            while self.pause:
                sleep(0.1)
            self.game.down()
            self.game.display()

if __name__=="__main__":
    Tetris()