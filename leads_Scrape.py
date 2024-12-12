import tkinter as tk
from tkinter import ttk, messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import threading
import time


class ApolloHunterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Apollo Hunter")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        self.delay = tk.IntVar(value=5)  # Default delay is 5 seconds
        self.recovered = 0
        self.running = False

        self.driver = None
        self.data = []  # Store scraped data

        # Fonts and colors
        font_title = ("Courier", 18, "bold")
        font_label = ("Helvetica", 12)
        bg_color = "#282C34"
        fg_color = "#61AFEF"

        self.root.config(bg=bg_color)

        # Title Label
        tk.Label(root, text="Apollo Hunter", font=font_title,
                 fg=fg_color, bg=bg_color).pack(pady=10)

        # Delay Input
        delay_frame = tk.Frame(root, bg=bg_color)
        delay_frame.pack(pady=5)
        tk.Label(delay_frame, text="Delay time (seconds):",
                 font=font_label, fg="white", bg=bg_color).pack(side=tk.LEFT)
        self.delay_entry = tk.Entry(
            delay_frame, textvariable=self.delay, width=10)
        self.delay_entry.pack(side=tk.LEFT, padx=5)

        # Start and Stop Buttons
        button_frame = tk.Frame(root, bg=bg_color)
        button_frame.pack(pady=10)
        self.start_button = tk.Button(
            button_frame, text="Start", bg="#98C379", font=font_label, command=self.start_scraping)
        self.start_button.pack(side=tk.LEFT, padx=10)
        self.stop_button = tk.Button(
            button_frame, text="Stop", bg="#E06C75", font=font_label, command=self.stop_scraping)
        self.stop_button.pack(side=tk.LEFT, padx=10)

        # Status Label
        self.status_label = tk.Label(
            root, text="Status: Ready", font=font_label, fg="white", bg=bg_color)
        self.status_label.pack(pady=10)

        # Progress Bar
        self.progress = ttk.Progressbar(
            root, orient=tk.HORIZONTAL, length=400, mode="indeterminate")
        self.progress.pack(pady=10)

        # Recovered Data Count
        tk.Label(root, text="Recovered Leads:", font=font_label,
                 fg="white", bg=bg_color).pack()
        self.recovered_label = tk.Label(root, text="0", font=(
            "Helvetica", 16), fg="#D19A66", bg=bg_color)
        self.recovered_label.pack(pady=5)

        # Data Display
        self.text_area = tk.Text(root, height=10, width=60, state=tk.DISABLED)
        self.text_area.pack(pady=10)

        # Save Button
        self.save_button = tk.Button(
            root, text="Save Data", bg="#61AFEF", font=font_label, command=self.save_data)
        self.save_button.pack(pady=10)

        # Initialize browser
        self.initialize_browser()

    def initialize_browser(self):
        """Launch Chrome and allow the user to log in."""
        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--start-maximized")
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.get("https://www.apollo.io")
            messagebox.showinfo(
                "Info", "Log in to Apollo.io and set the keyword link. Click 'Start' when ready."
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize browser: {e}")

    def start_scraping(self):
        """Start scraping leads."""
        if not self.driver:
            messagebox.showerror(
                "Error", "Browser is not initialized. Restart the application.")
            return

        if not self.running:
            self.running = True
            self.recovered = 0
            self.data = []
            self.update_status("Scraping in progress...")
            self.progress.start()
            self.start_button.config(state=tk.DISABLED)
            threading.Thread(target=self.scrape_data, daemon=True).start()
        else:
            messagebox.showinfo("Info", "Scraping is already running.")

    def stop_scraping(self):
        """Stop scraping and close the browser."""
        self.running = False
        self.update_status("Scraping stopped.")
        self.progress.stop()
        self.start_button.config(state=tk.NORMAL)

        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                messagebox.showinfo("Info", "Browser closed successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to close browser: {e}")

    def scrape_data(self):
        """Perform the scraping operation."""
        try:
            while self.running:
                # Locate all rows
                rows = self.driver.find_elements(By.XPATH, "//div[@role='row']")
                if not rows:
                    self.update_status("No rows found. Stopping.")
                    break

                # Iterate through each row and extract data
                for row in rows:
                    try:
                        name = row.find_element(By.XPATH, ".//a[@class='zp_p2Xqs zp_v565m']").text
                    except:
                        name = None

                    try:
                        role = row.find_element(By.XPATH, ".//span[@class='zp_xvo3G']").text
                    except:
                        role = None

                    try:
                        company = row.find_element(By.XPATH, ".//a[@class='zp_p2Xqs zp_v565m zp_REh41']").text
                    except:
                        company = None

                    try:
                        email = row.find_element(By.XPATH, ".//span[@data-has-tooltip='true']//span[@class='zp_xvo3G']").text
                    except:
                        email = None

                    lead_data = {
                        "name": name,
                        "role": role,
                        "company": company,
                        "email": email,
                    }

                    # Append data and update UI
                    self.data.append(lead_data)
                    self.recovered += 1
                    self.update_recovered_label()
                    self.update_text_area(f"{name}, {role}, {company}, {email}")

                # Click the "Next" button to go to the next page
                try:
                    next_button = self.driver.find_element(
                        By.XPATH, "//button[@aria-label='Next' and contains(@class, 'zp_qe0Li')]"
                    )
                    if next_button:
                        next_button.click()
                        self.update_status("Navigating to the next page...")
                    else:
                        self.update_status("No more pages to scrape. Stopping.")
                        break
                except Exception as e:
                    self.update_status(f"Error navigating pages: {e}")
                    break

                # Delay between requests
                time.sleep(self.delay.get())
        except Exception as e:
            messagebox.showerror("Error", f"Error during scraping: {e}")
        finally:
            self.stop_scraping()

    def update_recovered_label(self):
        """Update the recovered profiles count."""
        self.recovered_label.config(text=str(self.recovered))

    def update_text_area(self, lead_text):
        """Add lead text to the text area."""
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, lead_text + "\n")
        self.text_area.config(state=tk.DISABLED)

    def update_status(self, status):
        """Update the status label."""
        self.status_label.config(text=f"Status: {status}")

    def save_data(self):
        """Save scraped data to a text file."""
        try:
            with open("leads.txt", "w") as file:
                file.write("\n".join([str(lead) for lead in self.data]))
            messagebox.showinfo(
                "Info", "Data saved successfully to 'leads.txt'.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ApolloHunterApp(root)
    root.mainloop()