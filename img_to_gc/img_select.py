import img_to_gc
import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.ttk as ttk
import sys
import cv2 as cv
from PIL import Image,ImageTk
import threading
import time

root = tk.Tk()
root.configure(background='lightblue')
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

root.attributes('-fullscreen',True)

CHOOSEIMAGE = 0
TAKEPICTURE = 1

CHOOSEIMAGE_OK = 100
CHOOSEIMAGE_BACK = 101
GENERARE_CANNY = 110
GENERATE_GCODE = 111
GCODE_PLOT = 112

titlefont = int(screen_height/20) 

def waitBreak(choice):
    global canvas, choose_image_ok, choose_image_back, choose_image_ok_processing, t1
    if choice == CHOOSEIMAGE:

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
        
        if filename == "": 
            print("no file chosen")

        else:
            print(filename)
            clear(CHOOSEIMAGE)
            #img= (Image.open(filename))
            #resized_image= img.resize((300,205), Image.Resampling.LANCZOS)
            #new_image= ImageTk.PhotoImage(resized_image)
            #canvas.create_image(10,10, anchor=tk.NW, image=new_image

            # Create an object of tkinter ImageTk
            file = Image.open(filename)
            file = crop_image(file)
            file = file.resize((950,950))
            file.save(sys.path[0]+"\\image.jpg")
            img = ImageTk.PhotoImage(file)
            canvas= tk.Canvas(root, width= 1000, height= 1000, background='blue')
            canvas.create_image(
                500, 
                500, 
                anchor=tk.CENTER, 
                image=img
                )
            canvas.place(rely = 0.5, relx = 0.5, anchor=tk.CENTER)
            choose_image_ok = tk.Button(root, text="Continue", pady=5, font=("Arial Bold", titlefont),bg='lightgray', command=lambda: {waitBreak(CHOOSEIMAGE_OK)}, anchor=tk.CENTER)
            choose_image_ok.place(rely = 0.2, relx = 0.0, anchor=tk.NW)
            choose_image_back = tk.Button(root, text="Back", pady=5, font=("Arial Bold", titlefont),bg='lightgray', command=lambda: {waitBreak(CHOOSEIMAGE_BACK)}, anchor=tk.CENTER)
            choose_image_back.place(rely = 0.8, relx = 0.0, anchor=tk.SW)
            canvas['image'] = img #workaround because garbage collector why.
            
    if choice == CHOOSEIMAGE_OK:
        global t1
        print("image ok")
        clear(CHOOSEIMAGE_OK)
        choose_image_ok_processing = tk.Label(root, text = "Processing", pady=5, font=("Arial Bold", titlefont))
        choose_image_ok_processing.place(rely = 0.5, relx = 0.5, anchor=tk.CENTER)
        t1 = threading.Thread(target=generate_canny, args=())
        t1.start()
        
    if choice == CHOOSEIMAGE_BACK:
        print("image back")
        clear(CHOOSEIMAGE_BACK)
        main()

    if choice == TAKEPICTURE:
        print("take photo")
        clear(TAKEPICTURE)

def crop_image(image):
    file_image_width, file_image_height =  image.size
    if file_image_width == file_image_height:
        return image
    elif file_image_width > file_image_height: #crop x
        diff = file_image_width - file_image_height
        return image.crop((int(diff/2), 0, file_image_width-int(diff/2), file_image_height))
    else:#crop y
        diff = file_image_height - file_image_width
        return image.crop((0, int(diff/2), 0, file_image_height-int(diff/2)))

def generate_canny():
    global canvas, img, generate_gcode_processing
    canny = img_to_gc.img_to_svg(sys.path[0]+"\\image.jpg")
    cv.imwrite(sys.path[0]+"\\imageProcessed.png",canny)
    clear(GENERARE_CANNY)
    img = ImageTk.PhotoImage(file = sys.path[0]+"\\imageProcessed.png")
    canvas= tk.Canvas(root, width= 1000, height= 1000, background='blue')
    canvas.create_image(
        500, 
        500, 
        anchor=tk.CENTER, 
        image=img
        )
    canvas.place(rely = 0.5, relx = 0.5, anchor=tk.CENTER)
    generate_gcode_processing = tk.Label(root, text = "Generating G code", pady=5, font=("Arial Bold", titlefont))
    generate_gcode_processing.place(rely = 0.5, relx = 0.5, anchor=tk.CENTER)
    t2 = threading.Thread(target=generate_gcode, args=())
    t2.start()
    canvas['image'] = img #workaround because garbage collector why.

def generate_gcode():
    global t1
    t1.join()
    print ("Gcode gen")
    img_to_gc.generate_gcode()
    plot_gcode()

def plot_gcode():
    #plot gcode
    print("plot gcode")
    clear(GENERATE_GCODE)
    main()



def clear(page):
    if page == CHOOSEIMAGE or page == TAKEPICTURE:
        global main_choose_image, main_take_photo
        main_choose_image.place_forget()
        main_take_photo.place_forget()
        #main_exit.place_forget

    if page == CHOOSEIMAGE_BACK or page == CHOOSEIMAGE_OK:
        global canvas, choose_image_ok, choose_image_back
        canvas.place_forget()
        choose_image_ok.place_forget()
        choose_image_back.place_forget()

    if page == GENERARE_CANNY:
        global choose_image_ok_processing
        choose_image_ok_processing.place_forget()

    if page == GENERATE_GCODE:
        global generate_gcode_processing
        generate_gcode_processing.place_forget()

    if page == GCODE_PLOT:
        canvas.place_forget()



def EXIT():
    print("exit")
    root.destroy
    exit()

def main():
    global main_choose_image, main_take_photo, main_exit
    main_choose_image = tk.Button(root, text="Choose Image", pady=5, font=("Arial Bold", titlefont),bg='lightgray', command=lambda: {waitBreak(CHOOSEIMAGE)}, anchor=tk.CENTER)
    main_choose_image.place(rely = 0.5, relx = 0.3, anchor=tk.CENTER)
    main_take_photo = tk.Button(root, text="Take Photo", pady=5, font=("Arial Bold", titlefont),bg='lightgray', command=lambda: {waitBreak(TAKEPICTURE)}, anchor=tk.CENTER)
    main_take_photo.place(rely = 0.5, relx = 0.7, anchor=tk.CENTER)
    main_exit = tk.Button(root, text="Exit", pady=5, font=("Arial Bold", int(titlefont/3)),bg='lightgray', command=lambda: {EXIT()}, anchor=tk.CENTER)
    main_exit.place(rely = 0, relx = 1, anchor=tk.NE)

main()
root.mainloop()
    

    




canny = img_to_gc.img_to_svg(sys.path[0]+"\\image.jpg")



cv.imshow("canny", canny)
cv.waitKey(0)

img_to_gc.generate_gcode()