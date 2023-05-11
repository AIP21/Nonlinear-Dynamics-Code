from Lib.NewDEGraphics import *

win = DEGraphWin("Test", 800, 400, scale = 1)

print("a")


print("b")

with win:
    Label("EEE")
    
    print("c")

    win2 = Window(win, "Test2", 800, 400, scale = 1)
    with win2:
        
        print("d")

        Label("BBB")
    
    print("d")

    
win.mainloop()