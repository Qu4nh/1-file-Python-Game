from tkinter import *
from tkinter import messagebox
import webbrowser
win = Tk()
win.geometry("500x400+700+200")
win.title("Click sml")
 
global counter
counter = 0
multi=1

def Click():
    global counter
    counter=counter+multi
    Label1.config(text = counter,font="monospace 50")
    if Button1["bg"]=="black":
        Button1["bg"]="red"
    elif Button1["bg"]=="red":
        Button1["bg"]="orange"
    elif Button1["bg"]=="orange":
        Button1["bg"]="yellow"
    elif Button1["bg"]=="yellow":
        Button1["bg"]="lightgreen"
    elif Button1["bg"]=="lightgreen":
        Button1["bg"]="green"
    elif Button1["bg"]=="green":
        Button1["bg"]="aqua"
    elif Button1["bg"]=="aqua":
        Button1["bg"]="blue"
    elif Button1["bg"]=="blue":
        Button1["bg"]="purple"
    elif Button1["bg"]=="purple":
        Button1["bg"]="black"

url = "https://bit.ly/3EKsfdW"
url2 = "https://bit.ly/3Ag82da"
def update():
    global counter
    global multi
    if multi==1:
        if counter<50:
            messagebox.showerror(title="Chào =)) cre: QuAnh",message="Bạn cick cần 50 click")
        elif counter>=50:
            da1 = messagebox.askquestion(title="Upgrade", message="Bạn có muốn nâng cấp\nBạn sẽ bị trừ 40 điểm\n(Chơi đến cuối có điều bất ngờ 🤣)",icon="warning")
            if da1=="yes":
                multi=multi+1
                counter=counter-42
                messagebox.showinfo(title="Điểm multi +1",message="Vừa nãy: 1\nBây giờ: 2")
                   
            else:
                pass
    elif multi==2:
        if counter<100:
            messagebox.showerror(title="Khoan đã :))",message="Bạn cick cần 100 click")
        elif counter>=100:
            da2=messagebox.askquestion(title="Upgrade", message="Bạn có muốn nâng cấp\nBạn sẽ bị trừ 80 điểm",icon="warning")
            if da2=="yes":
                multi=multi+5
                counter=counter-87
                messagebox.showinfo(title="Điểm multi +5",message="Vừa nãy: 2\nBây giờ: 7")
            else:
                pass
    elif multi==7:
        if counter<1000:
            messagebox.showerror(title="Khoan đã :))",message="Bạn cick cần 1000 click")
        elif counter>=1000:
            da3=messagebox.askquestion(title="Upgrade", message="Bạn có muốn nâng cấp\nBạn sẽ bị trừ 900 điểm",icon="warning")
            if da3=="yes":
                multi=multi+50
                counter=counter-957
                messagebox.showinfo(title="Điểm multi +50",message="Vừa nãy: 7\nBây giờ: 57")
            else:
                pass
    elif multi==57:
        if counter<10000:
            messagebox.showerror(title="Khoan đã :))",message="Bạn cick cần 10000 click")
        elif counter>=10000:
            da3=messagebox.askquestion(title="Upgrade", message="Bạn có muốn nâng cấp\nBạn sẽ bị trừ 9999 điểm",icon="warning")
            if da3=="yes":
                multi=multi+100
                counter=counter-10156
                messagebox.showinfo(title="Điểm multi +5",message="Vừa nãy: 57\nBây giờ: 157")
            else:
                pass
    elif multi==157:
        if counter<999999999:
            da4=messagebox.askquestion(title="Thanks for playing", message="Cảm ơn vì đã chơi\nĐây là phần quà, bạn có lấy không?(Y/N)",icon="info")
            if da4=="yes":
                webbrowser.open(url)
            else:
                webbrowser.open(url2)
Label1 = Label(text="Điểm",font="monospace 10")
Label1.pack()
Label1 = Label(text="0",font="monospace 50")
Label1.pack() 
Button1 = Button(text = "Click", command = Click,font="monospace 50 bold", fg = "white", bg = "black")
Button1.pack()
Upgrade = Button(text = "upgrade", command = update,font="monospace 30 bold")
Upgrade.pack()
win.mainloop()