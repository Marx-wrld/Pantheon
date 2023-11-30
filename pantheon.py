import sys
sys.dont_write_bytecode = True
import tkinter as tk
import tkintermapview 
import tkinter.font as tkFont
from crawler import PantheonWebcam
from geo import IPGeolocation
from config import PantheonConfiguration
import threading 
import webview, webbrowser
import concurrent.futures
import re

__author__ = "Josh Schiavone"
__version__ = "1.0"

class Pantheon:
    def __init__(self, root):
        self.setup_window(root)
        self.create_widgets(root)

    def setup_window(self, root):
        width, height = 1261, 807
        screenwidth, screenheight = root.winfo_screenwidth(), root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % ((width, height, (screenwidth - width) / 2, (screenheight - height) / 2))
        root.geometry(alignstr)
        root.configure(bg="#000000")
        root.resizable(width=False, height=False)
        root.title(self.get_platform_title())
   
    def create_widgets(self, root):
        self.results_box = tk.Listbox(root, selectmode=tk.SINGLE)
        self.results_box2 = tk.Listbox(root, selectmode=tk.SINGLE)

        self.setup_results_box()
        self.results_box.bind("<Return>", self.browser_load_url)
        self.results_box.bind("<<ListboxSelect>>", self.add_ip_location)

        country_buttons = self.create_country_widgets(root)
        self.create_country_buttons(country_buttons)

        self.map_widget = tkintermapview.TkinterMapView(root, width=100, height=100, corner_radius=0)
        self.map_widget.place(x=650, y=470, width=530, height=300)
        self.map_widget.set_zoom(0)

        self.slider = tk.Scale(root, from_=30, to=300, orient=tk.HORIZONTAL, bg="#000000", fg="#ffffff", font=("Arial", 10))
        self.slider.place(x=950, y=95, width=260, height=40)

        slider_label = tk.Label(root, text="Crawling Verbosity (def=30): ", bg="#000000", fg="#ffffff", font=("Arial", 8))
        slider_label.place(x=800, y=95)

        PantheonConfiguration.PANTHEON_DEFAULT_COUNT = self.slider.get()

        centered_label = tk.Label(
            root, text="IOT Camera Links (<Enter> to view LIVE\u25CF feed): ", bg="#000000", fg="#ffffff", font=("Arial", 10)
        )

        centered_label.place(x=75, y=140)
        geo_label = tk.Label(
            root, text="Geolocation: ", bg="#000000", fg="#ffffff", font=("Arial", 10)
        )
        geo_label.place(x=650, y=140)

        http_data_label = tk.Label(
            root, text="Map View: ", bg="#000000", fg="#ffffff", font=("Arial", 10)
        )
        http_data_label.place(x=650, y=440)
        self.setup_labels(root)


    def setup_results_box(self):
        self.results_box.pack(fill=tk.BOTH, expand=True)
        self.results_box["bg"] = "#000000"
        self.results_box["borderwidth"] = "3px"
        ft = tkFont.Font(family="Arial", size=16)
        self.results_box["font"] = ft
        self.results_box["fg"] = "#9f9f9f"
        self.results_box["justify"] = "left"
        self.results_box.place(x=80, y=180, width=530, height=600)

        scrollbar = tk.Scrollbar(self.results_box, orient=tk.VERTICAL, activebackground="red")
        scrollbar.config(command=self.results_box.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_box.config(yscrollcommand=scrollbar.set)

        # create another results box to the right of the main one
        self.results_box2.pack(fill=tk.BOTH, expand=True)
        self.results_box2["bg"] = "#000000"
        self.results_box2["borderwidth"] = "3px"
        ft = tkFont.Font(family="Arial", size=12)
        self.results_box2["font"] = ft
        self.results_box2["fg"] = "#9f9f9f"
        self.results_box2.place(x=650, y=180, width=530, height=250)

    def create_country_buttons(self, country_buttons):
        x, y, row_height = 100, 5, 30
        for country, command in country_buttons.items():
            country_button = tk.Button(root, text=country, command=command, bg="#000000", fg="green", font=("Arial", 7, "bold"))
            country_button.place(x=x, y=y, width=90, height=25)
            x += 100

            if x > 1000:
                x = 100
                y += row_height

    def setup_labels(self, root):
        panthlabel = tk.Label(root, bg="#000000")
        ft = tkFont.Font(family="Terminal", size=14, weight="bold")
        panthlabel["font"] = ft
        panthlabel["fg"] = "#ffffff"
        panthlabel["justify"] = "center"
        panthlabel["text"] = "Pantheon."
        panthlabel.place(x=1150, y=0, width=100, height=37)

        p2label = tk.Label(root, bg="#000000", fg="green", font=("Arial Italic", 8), text="Insecure Camera Parser")
        p2label.place(x=1120, y=25, width=150, height=37)

        github_label = tk.Label(
            root, text="GitHub", fg="#ffffff", bg="#000000", cursor="hand2", underline=0, font=("Arial", 10, "italic")
        )
        github_label.bind("<Button-1>", self.open_github)
        github_label.place(x=10, y=780)

        legal_label = tk.Label(
            root, text="Ethical Notice", fg="#ffffff", bg="#000000", cursor="hand2", underline=0, font=("Arial", 10, "italic")
        )
        legal_label.bind("<Button-1>", self.open_legal)
        legal_label.place(x=75, y=780)

        copyright_label = tk.Label(
            root, text="Copyright (c) 2023 Josh Schiavone", fg="#ffffff", bg="#000000", cursor="hand2",
            font=("Arial", 10, "italic")
        )
        copyright_label.place(x=1050, y=780)

    def get_platform_title(self):
        if sys.platform == "win32":
            return f"Pantheon: Developed by {__author__} - Ver {__version__} - Pantheon user: Windows"
        elif sys.platform == "darwin":
            return f"Pantheon: Developed by {__author__} - Ver {__version__} - Pantheon user: MacOS"
        elif sys.platform == "linux":
            return f"Pantheon: Developed by {__author__} - Ver {__version__} - Pantheon user: Linux"
        else:
            return f"Pantheon - Developed by {__author__}"

    def create_country_widgets(self, root):
        return {
            "Canada": lambda: self.clear_and_execute_webcam("CA"),
            "USA": lambda: self.clear_and_execute_webcam("US"),
            "Mexico": lambda: self.clear_and_execute_webcam("MX"),
            "Brazil": lambda: self.clear_and_execute_webcam("BR"),
            "Romania": lambda: self.clear_and_execute_webcam("RO"),
            "Poland": lambda: self.clear_and_execute_webcam("PL"),
            "South Africa": lambda: self.clear_and_execute_webcam("ZA"),
            "France": lambda: self.clear_and_execute_webcam("FR"),
            "Russia": lambda: self.clear_and_execute_webcam("RU"),
            "Germany": lambda: self.clear_and_execute_webcam("DE"),
            "Finland": lambda: self.clear_and_execute_webcam("FI"),
            "China": lambda: self.clear_and_execute_webcam("CN"),
            "Japan": lambda: self.clear_and_execute_webcam("JP"),
            "Norway": lambda: self.clear_and_execute_webcam("NO"),
            "South Korea": lambda: self.clear_and_execute_webcam("KR"),
            "Taiwan": lambda: self.clear_and_execute_webcam("TW"),
            "Spain": lambda: self.clear_and_execute_webcam("ES"),
            "Netherlands": lambda: self.clear_and_execute_webcam("NL"),
            "United Kingdom": lambda: self.clear_and_execute_webcam("GB"),
            "Ireland": lambda: self.clear_and_execute_webcam("IE"),
            "Sweden": lambda: self.clear_and_execute_webcam("SE"),
            "Israel": lambda: self.clear_and_execute_webcam("IL"),
            "India": lambda: self.clear_and_execute_webcam("IN"),
            "Australia": lambda: self.clear_and_execute_webcam("AU"),
            "Italy": lambda: self.clear_and_execute_webcam("IT"),
            "Switzerland": lambda: self.clear_and_execute_webcam("CH"),
            "Belarus": lambda: self.clear_and_execute_webcam("BY"),
            "Iran": lambda: self.clear_and_execute_webcam("IR"),
            "Indonesia": lambda: self.clear_and_execute_webcam("ID"),
            "Estonia": lambda: self.clear_and_execute_webcam("EE"),
            "Czech Republic": lambda: self.clear_and_execute_webcam("CZ"),
            "Austria": lambda: self.clear_and_execute_webcam("AT"),
            "Belgium": lambda: self.clear_and_execute_webcam("BE"),
            "Bulgaria": lambda: self.clear_and_execute_webcam("BG"),
            "Serbia": lambda: self.clear_and_execute_webcam("RS"),
            "Ukraine": lambda: self.clear_and_execute_webcam("UA"),
            "Slovakia": lambda: self.clear_and_execute_webcam("SK"),
        }

    def open_github(self, event):
        github_url = "https://github.com/josh0xA/"
        webbrowser.open_new_tab(github_url)

    def open_legal(self, event):
        legal_url = "https://joshschiavone.com/"
        webbrowser.open_new_tab(legal_url)

    def browser_load_url(self, event):
        selected_index = self.results_box.curselection()[0]
        selected_url = self.results_box.get(selected_index)
        webbrowser.open_new(selected_url)

    def clear_results(self):
        self.results_box.delete(0, tk.END)
        PantheonConfiguration.webcams_found = []

    def clear_results2(self):
        self.results_box2.delete(0, tk.END)

    def clear_results3(self):
        self.results_box3.delete(0, tk.END)

    def apply_slider(self):
        PantheonConfiguration.PANTHEON_DEFAULT_COUNT = self.slider.get()

    def execute_webcam(self, country):
        self.loading_label = tk.Label(root, text="Loading...", font=("Arial", 12), fg="yellow", bg="black")
        self.loading_label.place(x=530, y=140)
        self.webcam_execute(country)

    def clear_and_execute_webcam(self, country):
        self.clear_results()
        self.execute_webcam(country)

    def webcam_execute(self, country):
        self.apply_slider()
        def crawl_and_display():
            PantheonConfiguration.num_webcams_found = 0
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(PantheonWebcam().crawl, country)
                future.result()  
                concurrent.futures.wait([future])              
            for webcam in PantheonConfiguration.webcams_found:
                PantheonConfiguration.num_webcams_found += 1
                self.results_box.insert(tk.END, webcam)
                self.results_box.itemconfig(tk.END, {"fg": "#18E63B"})
            self.loading_label.destroy()
        self.clear_results()
        self.clear_results2()

        threading.Thread(target=crawl_and_display).start()
    # add ip location to resultsbox2 on double click
    def add_ip_location(self, event):
        self.clear_results2()
        try:
            selected_index = self.results_box.curselection()[0]
            selected_ip = self.results_box.get(selected_index)
            selected_ip = re.sub(r'http://|https://|:\d+', '', selected_ip)
        except IndexError: pass # this handles the case where the user clicks an empty listbox
        try: 
            ip_location = IPGeolocation.get_location(selected_ip)
            if ip_location:
                self.results_box2.insert(tk.END, f"GeoDump for camera #{(selected_index + 1)}")
                self.results_box2.insert(tk.END, f"IP: {ip_location['ip']}")
                self.results_box2.insert(tk.END, f"City: {ip_location['city']}")
                self.results_box2.insert(tk.END, f"Region: {ip_location['region']}")
                self.results_box2.insert(tk.END, f"Country: {ip_location['country']}")
                self.results_box2.insert(tk.END, f"Latitude: {ip_location['latitude']}")
                self.results_box2.insert(tk.END, f"Longitude: {ip_location['longitude']}")
                self.results_box2.insert(tk.END, "---------------------------")
            
                self.map_widget.set_marker(ip_location['latitude'], ip_location['longitude'], 
                                        text=f"{ip_location['city']}, {ip_location['country']}",
                                        font=("Arial", 9), text_color="red", image_zoom_visibility=(0, float('inf')))
        except UnboundLocalError: pass # this is fine
            

    def get_http_data(self, event):
        import requests
        try:
            self.clear_results3()
            url = self.results_box.get(self.results_box.curselection()[0])
            response = requests.get(url)

            self.results_box3.insert(tk.END, f"HTTP Request URL: {response.url}\n")
            self.results_box3.insert(tk.END, f"HTTP Response Code: {response.status_code}\n")

            chunk_size = 80
            headers_text = str(response.headers)
            self.results_box3.insert(tk.END, "HTTP Headers:\n")
            for i in range(0, len(headers_text), chunk_size):
                self.results_box3.insert(tk.END, headers_text[i:i+chunk_size])

            chunk_size = 80
            response_text = response.text
            self.results_box3.insert(tk.END, "\nHTTP Response Text:\n")
            for i in range(0, len(response_text), chunk_size):
                self.results_box3.insert(tk.END, response_text[i:i+chunk_size])

        except Exception as e:
            pass  # do nothing


    def open_web_browser(self, url):
        webview.create_window('Pantheon Integrated Live Feed', url)
        webview.start(private_mode=True)

    def browser_load_url(self, event):
        selected_index = self.results_box.curselection()[0]
        selected_url = self.results_box.get(selected_index)
        
        self.open_web_browser(selected_url)

if __name__ == "__main__":
    root = tk.Tk()
    app = Pantheon(root)
    root.mainloop()