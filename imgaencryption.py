import tkinter as tk
from tkinter import *
from tkinter import messagebox as mg
from tkinter import filedialog as file
from PIL import Image, ImageTk
import os
import sqlite3

app = tk.Tk()
app.title("Encryption App")
app.geometry("900x600")
app.config(bg='#F5F5F5')  

ENCRYPTION_PASSWORD = None
ENCRYPTION_KEY = None

def file_browser():
    global fileses, img
    fileses = file.askopenfilename(initialdir=os.getcwd(), title='Select image',
                                   filetypes=(("PNG file", "*.png"),
                                              ('JPEG files', '*.jpg'), ('All files', '*.*')))

    if fileses:
        img = Image.open(fileses)
        img = ImageTk.PhotoImage(img)
        lbl.configure(image=img, width=200, height=200)
        lbl.image = img

def Encrypt():
    new = tk.Toplevel(app)
    new.geometry('500x300')
    new.config(bg='#F5F5F5')

    label = tk.Label(new, text='Enter the details', bg='#F5F5F5', fg='black', font=("Calibri", 15))
    label.grid(row=0, column=1, columnspan=1, pady=10)

    message = tk.Label(new, text="Key (Number):", fg='black', bg='#F5F5F5')
    message.grid(row=1, column=0, padx=65, pady=10, sticky='w')

    global filentry
    filentry = tk.Entry(new)
    filentry.grid(row=1, column=1, padx=10, pady=10, ipadx=30, ipady=6, sticky='w')

    passwords = tk.Label(new, text="Password:", fg='black', bg='#F5F5F5')
    passwords.grid(row=3, column=0, padx=65, pady=10, sticky='w')

    global passwordsentry
    passwordsentry = tk.Entry(new, show="@")
    passwordsentry.grid(row=3, column=1, padx=10, pady=10, ipadx=30, ipady=6, sticky='w')

    def ok():
        filepath = filentry.get()
        password = passwordsentry.get()
        con = sqlite3.connect('data.db')
        cur = con.cursor()
        exists = cur.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="users"')
        user_result = exists.fetchone()
        if user_result is None:
            cur.execute('CREATE TABLE users (password TEXT, key INTEGER)')
            cur.execute('INSERT INTO users (password, key) VALUES (?, ?)', (password, filepath))
            con.commit()
        else:
            cur.execute('INSERT INTO users (password, key) VALUES (?, ?)', (password, filepath))
            con.commit()
        con.close()
        
        encryptionimage(password, filepath)
        new.destroy()

    ok_button = tk.Button(new, text='OKEY', bg='red', fg='black', command=ok)
    ok_button.grid(row=7, column=0, columnspan=3, pady=27)

def encryptionimage(password, key):
    global fileses, ENCRYPTION_PASSWORD, ENCRYPTION_KEY
    print('The path of file:', fileses)
    print('Key for encryption:', key)

    try:
        key = int(key)
    except ValueError:
        mg.showerror("Error", "Key must be an integer")
        return
    
    ENCRYPTION_PASSWORD = password
    ENCRYPTION_KEY = key
    con = sqlite3.connect('data.db')
    cur = con.cursor()
    cur.execute('SELECT password, key FROM users WHERE password = ?', (ENCRYPTION_PASSWORD,))
    res = cur.fetchone()
    con.close()
    if res:
        if ENCRYPTION_PASSWORD == res[0] and ENCRYPTION_KEY == res[1]:
            if os.path.exists(fileses):
                with open(fileses, 'rb') as file:
                    image = bytearray(file.read())

                # XOR encryption with the provided key
                for index, value in enumerate(image):
                    image[index] = value ^ key

                # Show first 50 values of encrypted data for feedback
                a = ''.join(str(val) for val in image[:50])
                mg.showinfo('Encrypting Output', a)

                # Overwrite the original image with the encrypted data
                with open(fileses, 'wb') as encrypted_file:
                    encrypted_file.write(image)

                mg.showinfo('Success', 'Image encrypted successfully!')
            else:
                mg.showerror('Error', 'File not found!')
        else:
            mg.showerror('Error', 'Incorrect password or key!')

def Decrypt():
    new = tk.Toplevel(app)
    new.geometry('500x300')
    new.config(bg='#F5F5F5')

    label1 = tk.Label(new, text='Enter the details', bg='#F5F5F5', fg='black', font=("Calibri", 15))
    label1.grid(row=0, column=1, columnspan=1, pady=10)

    message1 = tk.Label(new, text="Key (Number):", fg='black', bg='#F5F5F5')
    message1.grid(row=1, column=0, padx=65, pady=10, sticky='w')

    global filentry1
    filentry1 = tk.Entry(new)
    filentry1.grid(row=1, column=1, padx=10, pady=10, ipadx=30, ipady=6, sticky='w')

    passworddecrypt = tk.Label(new, text="Password:", fg='black', bg='#F5F5F5',)
    passworddecrypt.grid(row=3, column=0, padx=65, pady=10, sticky='w')

    global passworddecryptentry
    passworddecryptentry = tk.Entry(new, show="@")
    passworddecryptentry.grid(row=3, column=1, padx=10, pady=10, ipadx=30, ipady=6, sticky='w')

    def ok():
        file_key = filentry1.get()
        password_input = passworddecryptentry.get()
        decryptionimage(password_input, file_key)
        new.destroy()

    ok_button = tk.Button(new, text='OKEY', bg='red', fg='black', command=ok)
    ok_button.grid(row=7, column=0, columnspan=3, pady=27)

def decryptionimage(password_input, key):
    global fileses, ENCRYPTION_PASSWORD, ENCRYPTION_KEY
    print('The path of file:', fileses)
    print('Key for decryption:', key)

    try:
        key = int(key)
    except ValueError:
        mg.showerror("Error", "Key must be an integer")
        return
    con = sqlite3.connect('data.db')
    cur = con.cursor()
    cur.execute('SELECT password, key FROM users WHERE password = ?', (password_input,))
    res1 = cur.fetchone()
    con.close()
    if res1:
        if password_input == res1[0] and key == res1[1]:
            if os.path.exists(fileses):
                # Open the encrypted image file as binary
                with open(fileses, 'rb') as encrypted_file:
                    image = bytearray(encrypted_file.read())

                # XOR decryption with the same key
                for index, value in enumerate(image):
                    image[index] = value ^ key

                # Show first 50 values of decrypted data for feedback
                a = ''.join(str(val) for val in image[:50])
                mg.showinfo('Decrypting Output', a)

                # Overwrite the encrypted image with the decrypted data
                with open(fileses, 'wb') as decrypted_file:
                    decrypted_file.write(image)

                mg.showinfo('Success', 'Image decrypted successfully!')
            else:
                mg.showerror('Error', 'File not found!')
        else:
            mg.showerror('Error', 'Incorrect password or key')

def bro():
    web.open()

mainlable = tk.Label(app, text='Steganography project', bg='#F5F5F5', fg='black', font=("Calibri", 25))
mainlable.pack()

infobutton = tk.Button(app, text='Project Info', bg='red', fg='black', font=("Calibri", 12), command=bro)
infobutton.pack(pady=20, ipadx=5, ipady=5)

lbl = Label(app, bg='black')
lbl.pack(pady=20, ipadx=35, ipady=35)

Button(lbl, text='Open Image', font='Arial 10 bold', bg='black', fg='white', command=file_browser).grid(row=2, column=2, ipadx=60, ipady=60)

frame1 = tk.Frame(app, bd=3, bg='gray', width=900, height=300, relief='flat')
frame1.pack(pady=30, ipadx=100, ipady=20)

mainbutton = tk.Button(frame1, text='Encrypt', bg='red', fg='black', font=("Calibri", 12), command=Encrypt)
mainbutton.pack(padx=10, pady=25, ipady=5, ipadx=10)

decryption = tk.Button(frame1, text='Decrypt', bg='red', fg='black', font=("Calibri", 12), command=Decrypt)
decryption.pack(padx=10, ipady=5, ipadx=10)

app.mainloop()

