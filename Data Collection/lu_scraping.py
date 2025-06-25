from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

about_url = "https://ul.edu.lb/en/about-us-history"
driver.get(about_url)

try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "p.before-pink-main.cairoreg.font15"))
    )
    paragraph_element = driver.find_element(By.CSS_SELECTOR, "p.before-pink-main.cairoreg.font15")
    print(paragraph_element.text) 
except (NoSuchElementException, TimeoutException) as e:
    print("Element not found or timed out:", e)

addmission_url = "https://ul.edu.lb/en/new-students/high-school-students#1651"
driver.get(addmission_url)

try:
    WebDriverWait(driver,10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR,".research-parag-details"))
    )
    ul_elements = driver.find_elements(By.CSS_SELECTOR, ".research-parag-details")

    for section_index, ul in enumerate(ul_elements, start=1):
        li_elements = ul.find_elements(By.TAG_NAME, "li")
        for index, li in enumerate(li_elements, start=1):
            print(li.text)
    
except (NoSuchElementException, TimeoutException) as e:
    print("Element not found or timed out:", e)

def process_section(driver, section_id):
    try:
        print(f"\n=== Processing section: {section_id} ===")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, section_id)))
        section = driver.find_element(By.ID, section_id)

        faculty_elements = section.find_elements(By.CLASS_NAME, "card-data-name")
        if not faculty_elements:
            print(f"[{section_id}] No faculty elements found.")
            return

        for index, faculty in enumerate(faculty_elements, start=1):
            link = faculty.find_element(By.TAG_NAME, "a")
            href = link.get_attribute("href")
            print(f"\n[{section_id}] Opening faculty link {index}: {href}")
            driver.get(href)

           
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            ol_elements = driver.find_elements(By.CSS_SELECTOR, "ol:not([style*='display: none'])")
            if ol_elements:
                li_elements = ol_elements[0].find_elements(By.TAG_NAME, "li")
                for li in li_elements:
                    print(li.text)
            else:
                print(f"[{section_id}] No visible <ol> found.")

         
            try:
                branch_cards = driver.find_elements(By.CLASS_NAME, "branches-card")
                for b_index, card in enumerate(branch_cards, start=1):
                    try:
                        address_title = card.find_element(By.XPATH, ".//h5[contains(text(), 'Address')]")
                        address_value = address_title.find_element(By.XPATH, "./following-sibling::div[1]")
                        print(f"Branch {b_index} Address: {address_value.text.strip()}")
                    except Exception as e:
                        print(f"Branch {b_index} - Address not found:", e)
            except Exception as e:
                print("Branch section not found:", e)

            
            driver.back()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, section_id)))
            section = driver.find_element(By.ID, section_id)
            faculty_elements = section.find_elements(By.CLASS_NAME, "card-data-name")

    except (NoSuchElementException, TimeoutException) as e:
        print(f"[{section_id}] Error:", str(e))

driver.get("https://ul.edu.lb/en/colleges-faculties-homepage")

section_ids = ["social", "tech"]  
for section_id in section_ids:
    process_section(driver, section_id)

driver.quit()