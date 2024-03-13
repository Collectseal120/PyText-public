import tkinter as tk
import random



class dice:
    def __init__(self,root, myID):
        self.root = root
        self.myID = myID
        self.myState = "unlocked"



        self.dice_button = tk.Button(self.root, text=self.myID, command=self.lock, width=4, height=1)
        self.dice_button.grid(row=self.myID,column=0, pady=5)



    def lock(self):
        if self.myState == "unlocked":
            self.myState = "locked"
            self.dice_button["background"] = "orange"
        elif self.myState == "locked":
            self.myState = "unlocked"
            self.dice_button["background"] = "white"


    def throw(self):
        if self.myState == "unlocked":
            self.dice_button["text"] = random.randint(1,6)

    def reset_locks(self):
        self.myState = "unlocked"
        self.dice_button["background"] = "white"






def start_throw():
    global current_player
    global current_player_throws
    if current_player_throws < 3:
        current_player_throws += 1
        for i in diceList:
            i.throw()
    else:
        for i in diceList:
            i.reset_locks()
        current_player_throws = 0
        if current_player == 1:
            current_player = 2
        else:
            current_player = 1
    player["text"] = "player "+str(current_player)
    


root = tk.Tk()
global current_player_throws
current_player_throws = 0
global current_player
current_player = 1
diceList = []
for i in range(5):
    diceList.append(dice(root, i))

roll = tk.Button(root, text="Roll!", command=start_throw)
roll.grid(row=6, column=0, pady=20, padx=100)

player = tk.Label(root, text="player "+str(current_player))
player.grid(row= 1, column=1,padx=50)
for i in diceList:
    i.reset_locks()
root.mainloop()






