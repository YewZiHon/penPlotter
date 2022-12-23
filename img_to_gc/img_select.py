import img_to_gc
import tkinter as tk
import tkinter.filedialog as filedialog
import sys
import cv2 as cv

root = tk.Tk()
root.configure(background='lightblue')
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

root.geometry(f'{screen_width}x{screen_height}+{0}+{0}')
root.attributes('-fullscreen',True)
while True:
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    okVar = tk.IntVar()

    CHOOSEIMAGE = 0
    TAKEPICTURE = 1
    EXIT = 999

    titlefont = int(screen_height/20)   
    image_source_choice = -1

    def waitBreak(okVar, choice):
        global image_source_choice
        okVar.set(1)
        image_source_choice = choice


    tk.Button(root, text="Choose Image", pady=5, font=("Arial Bold", titlefont),bg='lightgray', command=lambda: {waitBreak(okVar, CHOOSEIMAGE)}, anchor=tk.CENTER).place(rely = 0.5, relx = 0.3, anchor=tk.CENTER)
    tk.Button(root, text="Take Photo", pady=5, font=("Arial Bold", titlefont),bg='lightgray', command=lambda: {waitBreak(okVar, TAKEPICTURE)}, anchor=tk.CENTER).place(rely = 0.5, relx = 0.7, anchor=tk.CENTER)
    tk.Button(root, text="Exit", pady=5, font=("Arial Bold", int(titlefont/3)),bg='lightgray', command=lambda: {waitBreak(okVar, EXIT)}, anchor=tk.CENTER).place(rely = 0, relx = 1, anchor=tk.NE)

    root.tkraise()

    root.wait_variable(okVar)
    
    if image_source_choice == CHOOSEIMAGE:

        print("choose file")
        filetypes = (
        ('JPEG', '*.jpg'),
        ('PNG', '*.png'),
        ('Bitmap', '*.bmp')
        )

        filename = filedialog.askopenfilename(
            title='Open a file',
            initialdir='/',
            filetypes=filetypes)
        
        print(filename)

    if image_source_choice == TAKEPICTURE:
        print("taake photo")

    if image_source_choice == EXIT:
        print("exit")
        root.destroy

    




canny = img_to_gc.img_to_svg(sys.path[0]+"\\image.jpg")



cv.imshow("canny", canny)
cv.waitKey(0)

img_to_gc.generate_gcode()