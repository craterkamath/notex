import tkinter
from tkinter import *
from tkinter.scrolledtext import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter.simpledialog import askstring
import os
import string
import threading
import time
import pygame, sys,random,time
from pygame.locals import *

root = tkinter.Tk(className=" NoTeX v1.8")
'''root.tk.call('wm', 'iconphoto', root._w, image)
 root.iconbitmap(r'/home/crater/Desktop/DS_mini/icon.ico')
imgicon = PhotoImage(file=os.path.join(
    '/home/crater/Desktop/DS_mini', 'icon.ico'))
root.tk.call('wm', 'iconphoto', root._w, imgicon)'''  # Setting icon: Due for another day-> minutes spent = 25+10+30
# root.wm_iconbitmap('~/Desktop/DS_mini/icon.ico')
textPad = ScrolledText(root, width=80, height=50, bg="#DCEDC8")
textPad.configure(font=("sans-serif", 9, "normal"))
word = " "

main_stack = []
redo_stack = []

loadPercent = 0


def open_command():
    file = filedialog.askopenfile(
        parent=root, mode='rb', title='Select a file')
    if file != None:
        contents = file.read()
        textPad.delete('1.0', "end")
        textPad.insert('1.0', contents)
        file.close()


def save_command():
    file = filedialog.asksaveasfile(mode='w')
    if file != None:
        data = textPad.get('1.0', 'end-1c')
        file.write(data)
        file.close()


def exit_command():
    global root
    if messagebox.askokcancel("Quit", "Do you really want to quit?"):
        root.destroy()
        quit()


def about_command():
    lab = messagebox.showinfo(
        "About", "From the creators of UpperCase and Poseidon")


def new_command():
    result = messagebox.askquestion(
        "Save this!!", "Current changes unsaved. Do you want to Save?")
    if result == 'yes':
        save_command()
        textPad.delete('1.0', "end")
    else:
        textPad.delete('1.0', 'end')


def cut_command():
    textPad.event_generate("<<Cut>>")


def copy_command():
    textPad.event_generate("<<Copy>>")


def paste_command():
    textPad.event_generate("<<Paste>>")
#############################################################################

# all the charecters in the word tree will be stored in objects of the
# class node

#DATA structure 1

class node():

    def __init__(self, key, parent):
        self.key = key
        self.parent = parent
        self.children = []
        self.ch_val = []
        self.flag = 0
        self.children_count = 0


rt = []
i_suggest_list = []


def make_word_tree():
    

    
    wrd = [wd.rstrip('\n') for wd in open('words_alpha.txt')]
    #wrd = ["hello","yashas","yash","yamini","apple","appmaker","vishal","vinayak"]


    if(wrd != ""):

        # making the master root with its children
        for i in string.printable:
            temp = node(i, None)
            rt.append(temp)

        # '\n' is not present in the above list , thus added this to handle an exception when the word just has \n
        rt.append(node('\n', None))

        # getting the word's starting root from the master root array
        for w in wrd:

            for ch in rt:
                if(ch.key == w[0]):
                    temp_root = ch
                    break

            # if the one charecter itself is a word then , append it
            if(len(wrd) == 1):
                temp_root.flag = 1
            else:
                for i in range(1, len(w)):
                    if(w[i] not in temp_root.ch_val):
                        temp = node(w[i], temp_root)
                        temp_root.ch_val.append(w[i])
                        temp_root.children.append(temp)
                        temp_root.children_count += 1

                        # used for debugging
                        #print("INSERTED ", w[i], " after ", temp_root.key)
                    else:
                        for temp in temp_root.children:
                            if(temp.key == w[i]):
                                temp_root = temp

                    # if the word is inserted
                    if(i == len(w)-1):
                        temp.flag = 1

                        # used for debugging
                        #print("inserted")
                    temp_root = temp


def autosuggest(i_word):

    global i_suggest_list

    # everythime a new word is entered , clear the suggestion list and update
    # it again
    for i in range(0, len(i_suggest_list)):
        i_suggest_list.pop()

    # getting the word initial root in the master root list
    for i_temp in rt:
        if(i_temp.key == i_word[0]):
            i_temp_root = i_temp
            break

    i_adst = i_temp_root.key
    i_cflag = 1

    for i_i in range(1, len(i_word)):

        # if entered word is there in the tree
        if(i_word[i_i] in i_temp_root.ch_val):
            i_adst = i_adst+i_word[i_i]
            #print("added")
            for i_temp in i_temp_root.children:
                if(i_temp.key == i_word[i_i]):
                    i_temp_root = i_temp

        else:
            # if the entered word is not there in the word tree then dont show
            # anything
            i_cflag = 0
            for i in range(0, len(i_suggest_list)):
                i_suggest_list.pop()
            i_suggest_list.append(i_word)
            #print("didnt find")

    # used for debugging
    #print(i_temp_root.key)

    # if the currently entered word is valid
    if(i_cflag):
        i_suggest_list.append(i_adst)
        recursive_find(i_temp_root, i_adst[0:len(i_adst)-1])

    return i_suggest_list


def recursive_find(i_temp_root, cur_st):

    global i_suggest_list

    cur_st = cur_st + i_temp_root.key

    # if inbetween we get a flag then append that word to the final list
    if(i_temp_root.flag == 1):
        i_suggest_list.append(cur_st)

    # propogate till we reach a leaf node
    if(i_temp_root.children_count == 0):
        return

    else:
        for i_temp in i_temp_root.children:
            recursive_find(i_temp, cur_st)


#############################################################################

def check_change():
    # The text prediction and spellcheck part
    global predictions
    txt = ""
    txt = textPad.get('1.0', INSERT)
    global predictions
    if txt.split() != [] and txt[-1] != ' ':
        global word
        if word != txt.split()[-1]:
            word = txt.split()[-1]
            #print(word)       # word to be sent to the text prediction function

            # Undo and Redo part

            status = textPad.get('1.0', 'end-1c')

            if(len(main_stack) <= 100):
                main_stack.append(status)
            else:
                main_stack.pop(0)
                main_stack.append(status)

            #############################
            words = autosuggest(word.lower())
            if(words != []):
            	words = words[1:]
            #############################

            predictions.delete(0, END)
            predictions.insert(END, "Word:  "+word)
            for x in enumerate(words):
                predictions.insert(END, str(x[0]+1)+" : "+x[1])
    else:
        predictions.delete(0, END)

    root.update()


def undo_command():
    if(len(main_stack) > 0):
        redo_stack.append(main_stack.pop())
        textPad.delete('1.0', 'end')
        if(len(main_stack) > 0):
            textPad.insert('1.0', main_stack[-1])


def redo_command():
    if len(redo_stack) > 0:
        content = redo_stack.pop()
        main_stack.append(content)
        textPad.delete('1.0', 'end')
        textPad.insert('1.0', content)


def searchbox():
    global searchword
    global textPad

    textPad.tag_remove('found', '1.0', END)

    searchword = askstring("Search", "Enter the word to search:")

    if searchword == None or searchword == " ":
        return
    # print('{!r}'.format(start_pos))
    start_pos = '1.0'
    while start_pos:
        start_pos = textPad.search(
            searchword, start_pos, nocase=1, stopindex=END)
        if start_pos:
            end_pos = '{}+{}c'.format(start_pos, len(searchword))
            # print('{!r}'.format(end_pos))
            textPad.tag_add('found', start_pos, end_pos)
            start_pos = end_pos
    textPad.tag_config('found', foreground='red')


def replace():
    global replaceword
    global textPad
    global searchword
    if searchword:
        replaceword = askstring("Replace", "Enter the word to replace:")

        if(replaceword == None):
            textPad.tag_remove('found', '1.0', END)
            return
        '''
        x = []
        l = list(textPad.tag_ranges('found'))
        l.reverse()
        while l:
            x.append([l.pop(), l.pop()])
        for start, end in x:
            textPad.delete(start, end)
            textPad.insert(start, replaceword)
        '''
        lines = textPad.get('1.0', 'end-1c')
        lines = lines.split('\n')
        for i in range(len(lines)):
            while searchword in lines[i]:
                lines[i] = lines[i].replace(searchword, replaceword)
        txt = '\n'.join(lines)
        #print(searchword)
        #print(replaceword)
        #print(txt)
        textPad.delete('1.0', END)
        textPad.insert('1.0', txt)

        #redo_stack.append(txt)	


menu = Menu(root)
root.config(menu=menu)
filemenu = Menu(menu)
menu.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="New", command=new_command)
filemenu.add_command(label="Open", command=open_command)
filemenu.add_command(label="Save", command=save_command)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=exit_command)
editmenu = Menu(menu)
menu.add_cascade(label="Edit", menu=editmenu)
editmenu.add_command(label="Cut", command=cut_command)
editmenu.add_command(label="Copy", command=copy_command)
editmenu.add_command(label="Paste", command=paste_command)

helpmenu = Menu(menu)
menu.add_cascade(label="Help", menu=helpmenu)
helpmenu.add_command(label="About", command=about_command)

blankmenu = Menu(menu, tearoff=0)
menu.add_cascade(label="".ljust(130), menu=blankmenu)

menu.add_command(label="Search", command=searchbox)
menu.add_command(label="Replace", command=replace)
menu.add_command(label="Undo", command=undo_command)
menu.add_command(label="Redo", command=redo_command)

textPad.grid(row=0, column=0, columnspan=2)


frame = Frame(root)
frame.grid(row=0, column=3)
scrollbar = Scrollbar(frame, orient=VERTICAL)
predictions = Listbox(frame, width=40, height=40,
                      bg="#BBDEFB", yscrollcommand=scrollbar.set)
scrollbar.config(command=predictions.yview)
scrollbar.pack(side=RIGHT, fill=Y)
predictions.pack(side=LEFT, fill=BOTH, expand=1)

#################
''''
def screenLoad():
	pygame.init()
	height=768
	width=1366
	surface=pygame.display.set_mode((width,height))
	pygame.display.set_caption('NoteX v1.8')
	font2=pygame.font.SysFont(None,60)
	while not loadPercent:
		drawtext('Loading....',font2,window,WINDOWWIDTH//2,WINDOWHEIGHT//4)
		pygame.display.update()
	pygame.quit()
	sys.exit()
	pass

	


class buildTreeThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		make_word_tree()
		global loadPercent
		loadPercent = 1


class showLoadingScreen(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		screenLoad()


def drawtext1(text,font,surface,x,y):
    textobj=font.render(text,True,BLACK,YELLO)
    textrect=textobj.get_rect()
    textrect.centerx = x
    textrect.centery = y
    surface.blit(textobj,textrect)
    return(textrect)


t1 = time.time()


build = buildTreeThread()
loadScreen = showLoadingScreen()


build.start()
loadScreen.start()

build.join()
loadScreen.join()
'''
#################

#print(time.time() - t1)
t1 = time.time()
make_word_tree(	)
print("Tree building time : ",time.time() - t1)

while 1:
    check_change()
