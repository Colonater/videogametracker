import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import tkinter as tk
from tkinter import ttk, filedialog  # Import filedialog for saving and loading files
from PIL import Image, ImageTk  # Import PIL for image handling

# Create a Tkinter window
window = tk.Tk()
window.title("Hickey's eBay Price Scraper")
window.geometry("800x400")  # Set the window size

# Configure window colors
window.configure(bg="#333333")  # Light black background color

# Set window icon
chimchar_icon = Image.open("Chimchar.ico")
window.iconphoto(True, ImageTk.PhotoImage(chimchar_icon))

# Create a list to store the items and their data
items_data = []

# Define a function to get data from eBay
def get_data(searchterm):
    url = f'https://www.ebay.ca/sch/i.html?_from=R40&_nkw={searchterm}&_sacat=0&LH_PrefLoc=3&LH_Sold=1&LH_Complete=1&rt=nc&LH_BIN=1'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup

# Define a function to parse the eBay data
def parse(soup):
    productslist = []
    results = soup.find_all('div', {'class': "s-item__info clearfix"})  # "s-item__detail"
    for item in results:
        try:
            solddate = item.find('span', {'class': 's-item__title--tagblock'}).find('span').text
        except:
            solddate = ''
        try:
            bids = item.find('span', {'class': 's-item__bids'}).text
        except:
            bids = ''
        soldprice_str = item.find('span', {'class': 's-item__price'}).text.replace('C', '').replace('$', '').strip()
        soldprice = float(re.findall(r'\d+\.\d+', soldprice_str)[0])
        products = {
            'title': item.find('div', {'class': 's-item__title'}).text,
            'soldprice': soldprice,
            'solddate': solddate,
            'bids': bids,
            'link': item.find('a', {"class": 's-item__link'})['href'],
        }
        productslist.append(products)

    return productslist

# Define a function to update the GUI with items
def update_gui():
    searchterm = search_entry.get()
    soup = get_data(searchterm)
    productslist = parse(soup)
    output(productslist, searchterm)
    refresh_items()
    refresh_item_list()

# Define a function to add items to the list
def add_item(event=None):  # Allow Enter key to trigger this function
    searchterm = search_entry.get()
    items_data.append({'searchterm': searchterm})
    update_gui()
    search_entry.delete(0, tk.END)  # Clear the input field after adding an item

# Define a function to output data to a CSV file
def output(productslist, searchterm):
    productsdf = pd.DataFrame(productslist)
    csv_file = searchterm + "output.csv"
    productsdf.to_csv(csv_file, index=False)

# Define a function to calculate the average price from the CSV file
def calculate_average_price(csv_file, product_name):
    try:
        df = pd.read_csv(csv_file)
        filtered_df = df[df['title'].str.contains(product_name, case=False, regex=True)]
        if filtered_df.empty:
            return 0  # Return 0 for items with no data found
        average_price = filtered_df['soldprice'].mean()
        return average_price
    except Exception as e:
        return 0  # Return 0 for items with errors

# Define a function to refresh the items and update the total value
def refresh_items():
    for item_data in items_data:
        searchterm = item_data['searchterm']
        csv_file = searchterm + "output.csv"
        product_name = searchterm.replace('+', ' ')
        item_data['average_price'] = calculate_average_price(csv_file, product_name)

    total_value = sum(item_data['average_price'] for item_data in items_data)
    total_label.config(text=f"Total Value: ${total_value:.2f}")

# Define a function to refresh the item list
def refresh_item_list():
    item_list.delete(0, tk.END)
    for item_data in items_data:
        searchterm = item_data['searchterm']
        average_price = item_data.get('average_price', 0)
        item_list.insert(tk.END, (searchterm, f"${average_price:.2f}"))

# Define a function to delete selected items
def delete_item():
    selected_indices = item_list.curselection()
    for index in reversed(selected_indices):
        del items_data[index]
    update_gui()

# Define a function to save the program state with a custom file name and location
def save_state():
    save_path = filedialog.asksaveasfilename(
        initialdir="./saves",  # Initial directory for saving files (inside a "saves" folder)
        defaultextension=".txt",  # Default file extension for saving
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],  # Supported file types
        title="Save Program State",  # Dialog title
    )

    if save_path:
        with open(save_path, 'w') as file:
            for item_data in items_data:
                file.write(item_data['searchterm'] + '\n')

# Define a function to load the program state from a custom file name and location
def load_state():
    load_path = filedialog.askopenfilename(
        initialdir="./saves",  # Initial directory for loading files (inside a "saves" folder)
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],  # Supported file types
        title="Load Program State",  # Dialog title
    )

    if load_path:
        with open(load_path, 'r') as file:
            items_data.clear()  # Clear the existing data
            for line in file:
                searchterm = line.strip()
                items_data.append({'searchterm': searchterm})
        update_gui()

# Configure fonts and colors
label_font = ("Helvetica", 12)
entry_font = ("Helvetica", 12)
button_font = ("Helvetica", 12)

# Create and configure GUI elements
search_label = tk.Label(window, text="Enter a Product on eBay:", font=label_font, bg="#333333", fg="white")
search_label.pack(pady=(20, 5))

# Load images and create image objects
shinx_image = Image.open("shinx.png")
shinx_image = shinx_image.resize((100, 100), Image.LANCZOS)  # Resize image

shinx_photo = ImageTk.PhotoImage(shinx_image)

# Create labels to display images
shinx_label = tk.Label(window, image=shinx_photo, bg="#333333")
shinx_label.image = shinx_photo
shinx_label.pack()

search_entry = tk.Entry(window, font=entry_font)
search_entry.pack(pady=5)

add_button = tk.Button(window, text="Add Item", command=add_item, font=button_font, bg="purple", fg="white")
add_button.pack(pady=5)

total_label = tk.Label(window, text="Total Value: $0.00", font=label_font, bg="#333333", fg="white")
total_label.pack(pady=5)

item_list = tk.Listbox(window, font=label_font, selectmode=tk.MULTIPLE, width=50)
item_list.pack(expand=True, fill=tk.BOTH, padx=10)

button_frame = tk.Frame(window, bg="#333333")
button_frame.pack(pady=5)

refresh_button = tk.Button(button_frame, text="Refresh Prices", command=refresh_items, font=button_font, bg="purple", fg="white")
refresh_button.pack(side=tk.LEFT, padx=10)

delete_button = tk.Button(button_frame, text="Delete Selected", command=delete_item, font=button_font, bg="purple", fg="white")
delete_button.pack(side=tk.LEFT, padx=10)

save_button = tk.Button(button_frame, text="Save State", command=save_state, font=button_font, bg="purple", fg="white")
save_button.pack(side=tk.LEFT, padx=10)

# Create a Load State button
load_button = tk.Button(button_frame, text="Load State", command=load_state, font=button_font, bg="purple", fg="white")
load_button.pack(side=tk.LEFT, padx=10)

# Bind Enter key to add_item function
window.bind('<Return>', add_item)

# Load the program state if it exists
load_state()

# Start the GUI main loop
window.mainloop()
