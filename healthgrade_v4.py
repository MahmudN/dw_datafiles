from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import time
from webdriver_manager.chrome import ChromeDriverManager
import requests
import csv
import json
from urllib.parse import quote
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def parse_doctor_info(driver):
    doctors = driver.find_elements(By.CSS_SELECTOR, '.results-card--pro')
    data = []
    for doctor in doctors:
        try:
            name = doctor.find_element(By.CSS_SELECTOR, 'h3.card-name').text
            specialty = doctor.find_element(By.CSS_SELECTOR, "div.provider-info__specialty span:not(.sr-only)").text
            rating = doctor.find_element(By.CSS_SELECTOR, 'span.star-rating__score').text
            num_ratings = doctor.find_element(By.CSS_SELECTOR, 'span.star-rating__reviews').text
            address = doctor.find_element(By.CSS_SELECTOR, 'div.location-info.location-info--right-align address.location-info__address span.location-info-address__address').text
            feedback_items = doctor.find_elements(By.CSS_SELECTOR, 'li.provider-strengths__strength-item')
            feedback = [item.text for item in feedback_items]
            city_state_zip = doctor.find_element(By.CSS_SELECTOR, "div.location-info.location-info--right-align address.location-info__address span.location-info-address__city-state").text
            data.append({
                'Name': name,
                'Specialty': specialty,
                'Rating': rating,
                'Address': address,
                'City_State_Zip': city_state_zip,
                'Number_of_Ratings': num_ratings,
                'Patient_Feedback': feedback
            })
        except NoSuchElementException:
            continue
    return data

# Function to navigate to the next page
def navigate_next_page():
    try:
        # Locate the element you want to scroll to
        # Scroll to the element
        next_page_button = driver.find_element(By.CSS_SELECTOR, 'a[aria-label="Next Page"]')
        driver.execute_script("arguments[0].click();", next_page_button)
    except NoSuchElementException:
        print("Next page button not found or last page reached.")
        return False
    return True

# Function to navigate to the next page
def click_banner():
    try:
        # Locate the button by its I
        button = driver.find_element(By.ID, "onetrust-accept-btn-handler")
        # Click the button if it exists
        button.click()
        print("Button clicked successfully.")
    except NoSuchElementException:
        # Handle the case where the button does not exist
        print("Button not found.")
        return False
    return True

# get zip codes:
url = "https://raw.githubusercontent.com/MahmudN/dw_datafiles/main/zip_code_database.csv"
r = requests.get(url)
zip_dict = {}
lines = r.content.decode('utf-8').splitlines()

reader = csv.DictReader(lines)

for row in reader:
    key = row['zip']  # zip column is the key
    zip_dict[key] = row

specialty_list = """Immunopathology
Infectious Disease Medicine
Internal Medicine
Interventional Cardiology
Labor Coaching (Doula)
Laboratory Management Technology
Laboratory Medicine
Lactation Consulting
Legal Medicine
Marriage & Family Therapy
Massage Therapy
Mastectomy Fitting
Maternal-Fetal Medicine
Mechanotherapy
Medical Editing
Medical Ethics
Medical Examiner
Medical Informatics
Medical Microbiology
Medical Physics
Medical Technology
Medical Toxicology
Mental Health
Midwifery
Molecular Genetic Pathology
Music Therapy""".split("\n")

with open("healthgrade_output.json", 'w') as f:
    for specialty in specialty_list:

        for zcode in zip_dict.keys():




            # Initialize the WebDriver with Chrome options
            options = Options()
            options.headless = True  # Run in headless mode, remove this line if you want to see the browser
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)

            # Your target URL
            # URL = 'https://www.healthgrades.com/usearch?what=Family%20Medicine&entityCode=PS305&searchType=PracticingSpecialty&where=Bay%20Shore%2C%20NY&pt=40.64%2C-73.2&pageNum=1&sort.provider=bestmatch&state=NY&zip=11706'
            URL = f"https://www.healthgrades.com/usearch?what={quote(specialty)}&searchType=PracticingSpecialty&where={quote(zip_dict[zcode]['primary_city'])}%2C%20{quote(zip_dict[zcode]['state'])}&pt={quote(zip_dict[zcode]['latitude'])}%2C{quote(zip_dict[zcode]['longitude'])}&pageNum=1&sort.provider=bestmatch&state={quote(zip_dict[zcode]['state'])}&zip={zcode}"
            print(URL)
            
            driver.get(URL)  # Replace with the actual URL
            time.sleep(15)  # Wait for the dynamic content to load
            """
            

            # Wait for the element to be located and visible  --from ChatGPT
           # WebDriverWait(driver,20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div[data-qa-target="pagination--page-info"]')))

            banner_value = click_banner()


            # Extract total number of pages and store in 'temoin'
            page_info = driver.find_element(By.CSS_SELECTOR, 'div[data-qa-target="pagination--page-info"]').text
            temoin = int(page_info.split('of')[1].strip())
            print(f"Total number of pages: {temoin}")

            all_data = []
            current_page = 1
            # Loop to navigate through pages until reaching the 'temoin'
            while current_page <= temoin:
                time.sleep(5)  # Adjust based on your actual needs for page loading
                # Parse doctor info on the current page
                all_data.extend(parse_doctor_info(driver))
                if not navigate_next_page():
                    break  # Stop if the next page button is not found
                current_page += 1

            # Clean up
            driver.quit()

            # Output or process the collected data
            data_list = []
            for entry in all_data:
                print(entry)
                data_list.append(entry)

            print(len(data_list))

            json.dump(data_list)

            """