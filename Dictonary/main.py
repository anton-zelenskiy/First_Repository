from tkinter import *
import sqlite3
import random
from tkinter import messagebox

def Create(): # создание таблиц, не нужна
    cur = con.cursor()
    cur.execute("""CREATE TABLE EnWords (id_en INTEGER NOT NULL PRIMARY KEY,
                en_mean TEXT NOT NULL UNIQUE)""")
    con.commit()
    cur.execute("""CREATE TABLE RuWords (id_ru INTEGER NOT NULL PRIMARY KEY,
                ru_mean TEXT NOT NULL UNIQUE)""")
    con.commit()
    cur.execute("""CREATE TABLE Dictonary (id_dict INTEGER NOT NULL PRIMARY KEY,
                ru_word INTEGER NOT NULL,
                en_word INTEGER NOT NULL,
                is_known INTEGER,
                FOREIGN KEY (ru_word) REFERENCES RuWords (id_ru),
                FOREIGN KEY (en_word) REFERENCES EnWords (id_en))""")
    con.commit()

#--------------- Добавить в БД ---------------------------
def Insert(r, e):
    if text_ru.get() != '' and text_en.get() != '':
        cur = con.cursor()
        zero = 0
        cur.execute(""" INSERT INTO RuWords (ru_mean) VALUES (?) """, (r,))
        cur.execute(""" INSERT INTO EnWords (en_mean) VALUES (?) """, (e,))
        for args in [(r,e,zero)]:
            cur.execute(""" INSERT INTO Dictonary (ru_word, en_word, is_known)
                    VALUES ((SELECT id_ru FROM RuWords WHERE ru_mean = ?),
                            (SELECT id_en FROM EnWords WHERE en_mean = ?), ?)
                    """, args)
        con.commit()
        text_ru.delete(0, 'end')
        text_en.delete(0, 'end')

def Ok(event):
    Insert(text_ru.get(), text_en.get())
    win.destroy()

def Add(event):
    Insert(text_ru.get(), text_en.get())

def Cancel(event):
    win.destroy()

def ShowAddWindow():
    global win
    win = Toplevel(root)
    win.title("Добавить слово")
    win.minsize(width=400,height=200)
    win.maxsize(width=400,height=200)
    win.focus_set()
    win.grab_set()
    win.transient(root)

    panel = Frame(win, height = 200, width = 400)
    panel.pack(side = 'top', fill = 'both', expand = 1)

    label_ru = Label(panel, text = 'Русский эквивалент:', font = 'Arial 12')
    label_en = Label(panel, text = 'Английский эквивалент:', font = 'Arial 12')
    label_ru.place(x = 20, y = 30)
    label_en.place(x = 20, y = 60)

    global text_ru
    text_ru = Entry(panel, width = 20)
    global text_en
    text_en = Entry(panel, width = 20)
    text_ru.place(x = 210, y = 30)
    text_en.place(x = 210, y = 60)

    btn_ok = Button(panel, text = 'ОК')
    #btn_ok = Button(panel, text = 'ОК',
    #                command = lambda:
    #                Insert(text_ru.get(), #альтернативный варик для вызова события
    #                text_en.get()))
    btn_add = Button(panel, text = 'Еще...')
    btn_cancel = Button(panel, text = 'Отмена')

    btn_ok.bind("<ButtonRelease-1>", Ok)
    btn_add.bind("<ButtonRelease-1>", Add)
    btn_cancel.bind("<ButtonRelease-1>", Cancel)
    btn_ok.place(x = 20, y = 150, height = 30, width = 80)
    btn_add.place(x = 160, y = 150, height = 30, width = 80)
    btn_cancel.place(x = 300, y = 150, height = 30, width = 80)

#------------------------------------------------------

def Close():
    root.destroy()
    con.close()

def AllWords():
    global param
    param = ''

def KnownWords():
    global param
    param = '1'

def UnknownWords():
    global param
    param = '0'

def Random(source):
    random.seed( version = 2)
    try:
        rnd = random.choice(source)
        return rnd
    except IndexError:
        messagebox.showerror('Ошибка', 'Словарь неизученных слов пуст. Добавьте новые слова')
        return None

def GetCountDB():
    sel = con.cursor()
    sel.execute(""" SELECT COUNT(*) FROM Dictonary """)
    c = sel.fetchone()
    return list(c)

def GetIDsDB_(param):
    sel = con.cursor()
    if param == '':
        sel.execute(""" SELECT id_dict FROM Dictonary""")
    if param == '0':
        sel.execute(""" SELECT id_dict FROM Dictonary WHERE is_known = 0""")
    if param =='1':
        sel.execute(""" SELECT id_dict FROM Dictonary WHERE is_known = 1""")
    IDs = sel.fetchall()
    arr = []
    for i in IDs:
        arr.append(i[0])
    con.commit()
    return arr

def GetIDsDB():
    sel = con.cursor()
    sel.execute(""" SELECT id_dict FROM Dictonary""")
    IDs = sel.fetchall()
    arr = []
    for i in IDs:
        arr.append(i[0])
    con.commit()
    return arr


def GetTrueWord(param):
    sel = con.cursor()
    id_ = Random(GetIDsDB_(param))
    if id_ == None:
        return None
    else:
        sel.execute(""" SELECT Dictonary.en_word, Dictonary.ru_word,
                    EnWords.en_mean, RuWords.ru_mean FROM (Dictonary 
                    INNER JOIN EnWords ON
                    Dictonary.en_word = EnWords.id_en
                    INNER JOIN RuWords ON
                    Dictonary.ru_word = RuWords.id_ru)             
                    WHERE Dictonary.id_dict = ? """, (id_,))
        q = sel.fetchone()
        con.commit()
        return list(q)

def GetEnWord():
    sel = con.cursor()
    id_ = Random(GetIDsDB())
    sel.execute(""" SELECT EnWords.en_mean, EnWords.id_en FROM EnWords             
                    WHERE EnWords.id_en = ? """, (id_,))
    q = sel.fetchone()
    con.commit()
    return list(q)

def GetRuWord():
    sel = con.cursor()
    id_ = Random(GetIDsDB())
    sel.execute(""" SELECT RuWords.ru_mean, RuWords.id_ru FROM RuWords             
                    WHERE RuWords.id_ru = ? """, (id_,))
    q = sel.fetchone()
    con.commit()
    return list(q)

def Logic(param):
    quest= GetTrueWord(param)
    if quest == None:
        return None
    else:
        answer = [] # array answer
        id_trueword = 0 # id en or ru word in Dictonary
        choice = Random(quest[2:]) # 1,2 - id, 3,4 - words
        lang = ''
        if choice == quest[2]: # ru or en? - en
            id_trueword = quest[0]
            answer.append([quest[3], quest[1]])
            lang = 'en'
            while len(answer) != 4:     # забить массив ответов разными значениями
                arr = GetRuWord()       #
                if not arr in answer:   #
                    answer.append(arr)  #   
        elif choice == quest[3]: #ru
            id_trueword = quest[1]
            answer.append([quest[2], quest[0]])
            lang = 'ru'
            while len(answer) != 4:
                arr = GetEnWord()
                if not arr in answer:
                    answer.append(arr)    
        return [choice, answer, id_trueword, lang]

def Answer():
    id_true_word = id_unknown_word
    id_answer = int(var.get())
    if id_true_word == id_answer:
        ClearAnswers()
        for i in range(len(list_rbtn)):
            btn_val = list_rbtn[i].cget('value')
            if btn_val == id_true_word:
                list_rbtn[i].config(fg = 'green')
                che1.config(state = 'normal')
    else:
        ClearAnswers()
        for i in range(len(list_rbtn)):
            btn_val = list_rbtn[i].cget('value')
            if btn_val == id_answer:
                list_rbtn[i].config(fg = 'red')
                che1.config(state = 'disabled')

def ClearAnswers():
    for i in range(len(list_rbtn)):
        list_rbtn[i].config(fg = 'black')

def IfRemember(): # checkbox    
    id_remember_word = id_unknown_word
    sel = con.cursor()
    sql = """ UPDATE Dictonary SET is_known = ? WHERE en_word = ?"""
    if c1.get() == 1:
        if lang == 'en':
            sel.execute(sql, (1, id_remember_word))          
        else:
            sel.execute(sql, (1, id_remember_word))
    else:
        if lang == 'en':
            sel.execute(sql, (0, id_remember_word))
        else:
            sel.execute(sql, (0, id_remember_word))
    con.commit()
           
def Next(event):
    ClearAnswers()
    che1.config(state = 'disabled')
    res = Logic(param)
    if res == None:
        return
    else:
        global id_unknown_word
        global lang
        global possible_answers
        unknown_word.set(res[0])  # отгадываемое слово
        possible_answers = res[1] # возможные ответы
        id_unknown_word = res[2]  # id отгадываемго слова
        lang = res[3] # язык отгадываемого слова
        
        head_word.config(textvariable = unknown_word)
        
        temp = []
        for i in range(len(list_rbtn)):
            while True:
                rnd = random.randint(0,3)
                word, id_word = possible_answers[rnd]
                if not rnd in temp:
                    list_rbtn[i].config(text=word, variable = var, value=id_word)
                    temp.append(rnd)
                    break
                else:
                    continue
        var.set(0)
        che1.deselect()

root = Tk()
root.title('Перевод')
x = (root.winfo_screenwidth() - root.winfo_reqwidth()) // 2
y = (root.winfo_screenheight() - root.winfo_reqheight()) // 2
root.geometry("+%d+%d" % (x, y))
root.minsize(width=400, height = 300)
root.maxsize(width=400, height = 300)
panelFrame = Frame(root, height = 300, width = 400, bg = 'white')
panelFrame.pack(side = 'top', fill = 'both', expand = 1)

m = Menu(root)
root.config(menu=m)
fm = Menu(m)
m.add_cascade(label="Файл",menu=fm)
fm.add_command(label="Добавить слово", command = ShowAddWindow)
sub_menu = Menu(fm)
fm.add_cascade(label="Режим", menu=sub_menu)
sub_menu.add_command(label = "Все слова", command = AllWords)
sub_menu.add_command(label = "Новые слова", command = UnknownWords)
sub_menu.add_command(label = "Повторить выученные слова", command = KnownWords)
fm.add_command(label="Выход", command = Close)
hm = Menu(m)
m.add_cascade(label="Дополнительно",menu=hm)
hm.add_command(label="О программе", command = '')

con = sqlite3.connect("dict.db")

unknown_word = StringVar()
param = ''
res = Logic(param)
unknown_word.set(res[0])    # отгадываемое слово
possible_answers = res[1]   # возможные ответы
id_unknown_word = res[2]    # id отгадываемго слова
lang = res[3]               # язык отгадываемого слова

head_word = Label(panelFrame, font = 'Arial 18',
                  textvariable = unknown_word, bg = 'white')
head_word.place(x = 130, y = 15) 

#-------- распределить ответы рандомно в checkbox -----------
var = StringVar()
list_rbtn = []
temp = []
j = 0
while len(temp) != 4:
    rnd = random.randint(0,3)
    word, id_word = possible_answers[rnd]
    if not rnd in temp:
        list_rbtn.append(Radiobutton(panelFrame, text=word, variable=var,
                        font = 'Arial 14', value=id_word, bg = 'white',
                        indicatoron = 0, command = Answer))
        temp.append(rnd)
for z in range(len(list_rbtn)):
    list_rbtn[z].place(x = 130, y = 55 + j)
    j += 40
#--------------------------------------------------------------

c1 = IntVar()
che1 = Checkbutton(panelFrame,text='Запомнил', variable=c1,
                   onvalue=1, offvalue=0, bg = 'white', 
                   state = 'disabled', command = IfRemember)
che1.place(x = 130, y = 230)

btn_next = Button(panelFrame, text = '---->', bg = '#afffaf')
btn_next.bind("<ButtonRelease-1>", Next)
btn_next.place(x = 230, y = 115, height = 30, width = 80)

root.mainloop()
