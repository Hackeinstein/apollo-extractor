    def scrape_data(self):
        """Perform the scraping operation."""
    
        try:
            with open("link.txt", "r") as file:
                link = file.read()
                
        except Exception as e:
            logging.error(f"Error reading link: {e}")
            self.update_status("No link found. Stopping.")
            self.stop_scraping()

        row_counter=1
        

        try:
            while self.running:

                self.driver.get(link)
                
                # Wait for rows to appear
                
                #check if its time to go next page
                if row_counter % 25 == 0:
                    try:
                        next_button = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(By.XPATH, "//button[@aria-label='Next' and contains(@class, 'zp_qe0Li')]"))
                        if next_button:
                            next_button.click()
                            self.update_status("Navigating to the next page...")
                        else:
                            self.update_status("No more pages to scrape. Stopping.")
                            self.stop_scraping()
                    except Exception as e:
                        self.update_status(f"Error navigating pages: {e}")
                        break
                else:
                    # loads rows
                    try:
                        rows = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_all_elements_located((By.XPATH, "//div[@role='row']"))
                        )
                        print(f"gotten rows: {len(rows)}")
                    except Exception as e:
                        logging.error(f"Error locating rows: {e}")
                        self.update_status("No rows found. Stopping.")
                        break

                    
                    if not self.running:
                        break

                    row = rows[row_counter]

                    hr_name, hr_email, employee_name, employee_role = None, None, None, None

                    try: # row block
                        # Locate and click the HR name
                        name_element = row.find_element(By.XPATH, ".//a[contains(@class, 'zp_p2Xqs')]")
                        hr_name = name_element.text.split(" ")[0]
                        name_element.click()

                        # Wait for the "Access Email & Phone Number" button and click it
                        try:
                                access_button = WebDriverWait(self.driver, 5).until(
                                    EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'zp-button') and .//div[contains(text(), 'Access Email')]]"))
                                )
                                if access_button:
                                    access_button.click()

                                print(f"Access button clicked for {hr_name}")
                        except Exception as e:
                                pass
                        try:
                            #Retrieve email
                            email_element = WebDriverWait(self.driver, 5).until(
                                EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'zp-link') and contains(@class, 'zp_d0CTE') and contains(@class, 'zp_N3Yvt') and contains(@class, 'zp_kOWmA')]"))
                            )
                            hr_email = email_element.text
                            print(f"Email found for {hr_name}: {hr_email}")
                        except Exception as e:
                            logging.warning(f"Email not found for {hr_name}: {e}")

                    
                           
                        # Retrieve employee data
                        try:
                            leads_btn = self.driver.find_element(By.XPATH, "//a/span[text()='Find Leads']")
                            leads_btn.click()

                            employee_rows = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_all_elements_located((By.XPATH, "//tr[@data-cy='SelectableTableRow']"))
                            )
                            first_row = employee_rows[random.randint(1, len(employee_rows) - 1)]
                            employee_name = first_row.find_element(By.XPATH, ".//a[contains(@href, '/people/')]").text
                            employee_role = first_row.find_element(By.XPATH, ".//span[@class='zp_xvo3G']").text
                        except Exception as e:
                            logging.warning(f"Employee data not found for {hr_name}: {e}")

                    except Exception as e:
                        logging.error(f"Error processing row: {e}")

                    # Store and update data
                    
                    lead_data = f"{hr_name}\n{hr_email}\n{employee_name}\n{employee_role}\n=================================" 
                    self.data.append(lead_data)
                    row_counter += 1
                    self.recovered += 1
                    self.update_recovered_label()
                    self.update_text_area(f"{lead_data}")

                    # Delay between requests
                    time.sleep(self.delay.get())
            

            # end of while loop
            

        except Exception as e:
            messagebox.showerror("Error", f"Error during scraping: {e}")
        finally:
            self.stop_scraping()