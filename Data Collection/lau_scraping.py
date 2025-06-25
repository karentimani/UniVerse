from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import json

# Set up the Selenium WebDriver
driver = webdriver.Chrome()

# Initialize the main data dictionary
university_data = {
    "university_link": "https://www.lau.edu.lb",
    "locations": [],
    "about": {"mission": "", "values": {"intro": "", "list": []}},
    "admission_requirements": [],
    "tuition_aid": [],
    "programs": [],
    "tuition_fees_aid": []
}

try:
    driver.get("https://www.lau.edu.lb")
    locations_url = "https://www.lau.edu.lb/about/locations/"
    driver.get(locations_url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.grid"))
    )
    location_elements = driver.find_elements(By.CSS_SELECTOR, "div.grid a")
    university_data["locations"] = [element.text.strip() for element in location_elements if element.text.strip() != ""]

    pages = [
        {"url": "https://www.lau.edu.lb/about/mission.php", "name": "Mission"},
        {"url": "https://catalog.lau.edu.lb/2024-2025/undergraduate/programs/", "name": "Programs"},
        {"url": "https://catalog.lau.edu.lb/2024-2025/undergraduate/tuition.php", "name": "TuitionFeesAid"},
        {"url": "https://catalog.lau.edu.lb/2024-2025/undergraduate/admission.php", "name": "AdmissionRequirements"},
        {"url": "https://catalog.lau.edu.lb/2024-2025/undergraduate/tuition-fees-aid.php", "name": "TuitionAid"}
    ]

    for page in pages:
        driver.get(page["url"])

        if page["name"] == "Mission":
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h2"))
            )
            sections = driver.find_elements(By.TAG_NAME, "h2")
            for section in sections:
                if section.text == "LAU Mission":
                    next_p = section.find_element(By.XPATH, "following-sibling::p")
                    university_data["about"]["mission"] = next_p.text.strip()
                elif section.text == "LAU Values":
                    next_p = section.find_element(By.XPATH, "following-sibling::p")
                    university_data["about"]["values"]["intro"] = next_p.text.strip()
                    try:
                        ul = next_p.find_element(By.XPATH, "following-sibling::ul")
                        li_items = ul.find_elements(By.TAG_NAME, "li")
                        university_data["about"]["values"]["list"] = [li.text.strip() for li in li_items if li.text.strip() != ""]
                    except NoSuchElementException:
                        pass

        elif page["name"] == "Programs":
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h2"))
            )
            school_headers = driver.find_elements(By.TAG_NAME, "h2")
            schools = [{"name": header.text.strip()} for header in school_headers if "School of" in header.text]
            programs_list = []
            for school in schools:
                school_dict = {"name": school['name'], "majors": [], "minors": []}
                header_element = driver.find_element(By.XPATH, f"//h2[text()='{school['name']}']")
                ul = header_element.find_element(By.XPATH, "following-sibling::ul")
                li_items = ul.find_elements(By.TAG_NAME, "li")
                programs = []
                for li in li_items:
                    try:
                        link = li.find_element(By.TAG_NAME, "a")
                        program_name = link.text.strip()
                        program_link = link.get_attribute("href")
                        if program_name and program_link:
                            programs.append({"name": program_name, "link": program_link})
                    except NoSuchElementException:
                        continue

                try:
                    minors_em = ul.find_element(By.XPATH, f"following::em[text()='Minors' and (not(following::h2) or following::h2[1][text()!='{school['name']}'])]")
                    minors_ul = minors_em.find_element(By.XPATH, "following::ul[1]")
                    minors_li_items = minors_ul.find_elements(By.TAG_NAME, "li")
                    minors = []
                    for li in minors_li_items:
                        try:
                            link = li.find_element(By.TAG_NAME, "a")
                            minor_name = link.text.strip()
                            minor_link = link.get_attribute("href")
                            if minor_name and minor_link:
                                minors.append({"name": minor_name, "link": minor_link})
                        except NoSuchElementException:
                            continue
                except NoSuchElementException:
                    minors = []

                for program in programs:
                    driver.get(program["link"])
                    try:
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "tabs")))
                        overview_content = []
                        try:
                            overview_tab = driver.find_element(By.XPATH, "//div[@class='tabs']//a[contains(text(), 'Overview')]")
                            driver.execute_script("arguments[0].click();", overview_tab)
                            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "tab0")))
                            overview_section = driver.find_element(By.ID, "tab0")
                            overview_paragraphs = overview_section.find_elements(By.TAG_NAME, "p")
                            overview_content = [p.text.strip() for p in overview_paragraphs if p.text.strip()]
                        except (NoSuchElementException, TimeoutException):
                            pass

                        curriculum_content = []
                        try:
                            curriculum_tab = driver.find_element(By.XPATH, "//div[@class='tabs']//a[contains(text(), 'Curriculum')]")
                            driver.execute_script("arguments[0].click();", curriculum_tab)
                            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "tab4")))
                            curriculum_section = driver.find_element(By.ID, "tab4")
                            curriculum_elements = curriculum_section.find_elements(By.XPATH, "./*")
                            for element in curriculum_elements:
                                tag = element.tag_name
                                text = element.text.strip()
                                if not text:
                                    continue
                                if tag == "h2":
                                    curriculum_content.append(f"H2: {text}")
                                elif tag == "h3":
                                    curriculum_content.append(f"H3: {text}")
                                elif tag == "p":
                                    curriculum_content.append(f"Paragraph: {text}")
                                elif tag == "ul":
                                    curriculum_content.append("List:")
                                    li_items = element.find_elements(By.TAG_NAME, "li")
                                    for li in li_items:
                                        if li.text.strip():
                                            curriculum_content.append(f"- {li.text.strip()}")
                                else:
                                    curriculum_content.append(f"{tag.upper()}: {text}")
                        except (NoSuchElementException, TimeoutException):
                            pass

                        major_dict = {
                            "name": program['name'],
                            "overview": overview_content,
                            "curriculum": curriculum_content
                        }
                        school_dict["majors"].append(major_dict)
                    finally:
                        driver.get(page["url"])
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h2")))

                for minor in minors:
                    driver.get(minor["link"])
                    try:
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "tabs")))
                        overview_content = []
                        try:
                            overview_tab = driver.find_element(By.XPATH, "//div[@class='tabs']//a[contains(text(), 'Overview')]")
                            driver.execute_script("arguments[0].click();", overview_tab)
                            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "tab0")))
                            overview_section = driver.find_element(By.ID, "tab0")
                            overview_paragraphs = overview_section.find_elements(By.TAG_NAME, "p")
                            overview_content = [p.text.strip() for p in overview_paragraphs if p.text.strip()]
                        except (NoSuchElementException, TimeoutException):
                            pass

                        curriculum_content = []
                        try:
                            curriculum_tab = driver.find_element(By.XPATH, "//div[@class='tabs']//a[contains(text(), 'Curriculum')]")
                            driver.execute_script("arguments[0].click();", curriculum_tab)
                            WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "tab4")))
                            curriculum_section = driver.find_element(By.ID, "tab4")
                            curriculum_elements = curriculum_section.find_elements(By.XPATH, "./*")
                            for element in curriculum_elements:
                                tag = element.tag_name
                                text = element.text.strip()
                                if not text:
                                    continue
                                if tag == "h2":
                                    curriculum_content.append(f"H2: {text}")
                                elif tag == "h3":
                                    curriculum_content.append(f"H3: {text}")
                                elif tag == "p":
                                    curriculum_content.append(f"Paragraph: {text}")
                                elif tag == "ul":
                                    curriculum_content.append("List:")
                                    li_items = element.find_elements(By.TAG_NAME, "li")
                                    for li in li_items:
                                        if li.text.strip():
                                            curriculum_content.append(f"- {li.text.strip()}")
                                else:
                                    curriculum_content.append(f"{tag.upper()}: {text}")
                        except (NoSuchElementException, TimeoutException):
                            pass

                        minor_dict = {
                            "name": minor['name'],
                            "overview": overview_content,
                            "curriculum": curriculum_content
                        }
                        school_dict["minors"].append(minor_dict)
                    finally:
                        driver.get(page["url"])
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "h2")))

                programs_list.append(school_dict)
            university_data["programs"] = programs_list

        elif page["name"] == "TuitionFeesAid":
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "content"))
            )
            content_section = driver.find_element(By.ID, "content")
            all_elements = content_section.find_elements(By.XPATH, "./*")
            content_list = []
            for element in all_elements:
                if element.tag_name == "table":
                    rows = element.find_elements(By.TAG_NAME, "tr")
                    table_content = []
                    for row in rows:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if not cells:  # Likely a header row
                            headers = row.find_elements(By.TAG_NAME, "th")
                            if headers:
                                table_content.append([header.text.strip() for header in headers if header.text.strip()])
                        else:
                            table_content.append([cell.text.strip() for cell in cells if cell.text.strip()])
                    content_list.append({"table": table_content})
                elif element.tag_name in ["h2", "h3", "h4"]:
                    content_list.append(f"{element.tag_name.upper()}: {element.text.strip()}")
                elif element.tag_name == "p":
                    if element.text.strip():
                        content_list.append(f"Paragraph: {element.text.strip()}")
                elif element.tag_name == "ul":
                    content_list.append("Bullet Points:")
                    li_items = element.find_elements(By.TAG_NAME, "li")
                    for li in li_items:
                        if li.text.strip():
                            content_list.append(f"- {li.text.strip()}")
                else:
                    if element.text.strip():
                        content_list.append(f"{element.tag_name}: {element.text.strip()}")
            university_data["tuition_fees_aid"] = content_list

        elif page["name"] == "TuitionAid":
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "content"))
            )
            content_section = driver.find_element(By.ID, "content")
            all_elements = content_section.find_elements(By.XPATH, "./*")
            content_list = []
            for element in all_elements:
                if element.tag_name in ["h2", "h3", "h4"]:
                    content_list.append(f"{element.tag_name.upper()}: {element.text.strip()}")
                elif element.tag_name == "p":
                    if element.text.strip():
                        content_list.append(f"Paragraph: {element.text.strip()}")
                elif element.tag_name == "table":
                    content_list.append("Table: [content not parsed]")
                elif element.tag_name == "ul":
                    content_list.append("Bullet Points:")
                    li_items = element.find_elements(By.TAG_NAME, "li")
                    for li in li_items:
                        if li.text.strip():
                            content_list.append(f"- {li.text.strip()}")
                else:
                    if element.text.strip():
                        content_list.append(f"{element.tag_name}: {element.text.strip()}")
            university_data["tuition_aid"] = content_list

        elif page["name"] == "AdmissionRequirements":
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "content"))
            )
            content_section = driver.find_element(By.ID, "content")
            content_list = []
            try:
                start_h2 = content_section.find_element(By.XPATH, ".//h2[contains(text(), 'Admission Requirements')]")
                content_list.append(f"H2: {start_h2.text.strip()}")
                next_elements = start_h2.find_elements(By.XPATH, "following-sibling::*")
                for element in next_elements:
                    if element.tag_name == "p" and "All submitted documents" in element.text:
                        if element.text.strip():
                            content_list.append(f"Paragraph: {element.text.strip()}")
                        break
                    elif element.tag_name in ["h3", "h4"]:
                        content_list.append(f"{element.tag_name.upper()}: {element.text.strip()}")
                    elif element.tag_name == "p":
                        if element.text.strip():
                            content_list.append(f"Paragraph: {element.text.strip()}")
                    elif element.tag_name == "ul":
                        content_list.append("Bullet Points:")
                        li_items = element.find_elements(By.TAG_NAME, "li")
                        for li in li_items:
                            if li.text.strip():
                                content_list.append(f"- {li.text.strip()}")
                    else:
                        if element.text.strip():
                            content_list.append(f"{element.tag_name}: {element.text.strip()}")
            except NoSuchElementException:
                content_list.append("Admission Requirements section not found")
            university_data["admission_requirements"] = content_list

finally:
    driver.quit()

# Save to JSON file
with open("lau_data.json", "w") as f:
    json.dump(university_data, f, indent=4)