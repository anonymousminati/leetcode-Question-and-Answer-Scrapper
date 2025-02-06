from datetime import datetime

import undetected_chromedriver as uc
import json
import time
import os
import re

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TIME_DELAY = 3

# Initialize undetected_chromedriver options
options = uc.ChromeOptions()
# For testing login, do not run headless so you can manually handle any prompts
# options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Set a custom user agent to mimic a real browser
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
options.add_argument(f"--user-agent={user_agent}")

# OPTIONAL: Use a persistent Chrome profile to bypass the login flow manually.
# If you encounter issues, try commenting out these two lines.
# options.add_argument("--user-data-dir=C:/Users/prath/AppData/Local/Google/Chrome/User Data")
# options.add_argument("--profile-directory=Default")
options.add_argument("--disable-extensions")

# Initialize undetected_chromedriver inside a try/except block
try:
    # Optionally, specify the main Chrome version (if you know it, e.g., version_main=112)
    CODE_DRIVER = uc.Chrome(options=options, version_main=132)
except Exception as e:
    print("Error initializing undetected_chromedriver:", e)
    exit(1)
def make_directory(path):
    """Creates a directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)

def save_json(data, filename="leet_code_solutions.json"):
    """Saves the given data to a JSON file and maintains a backup."""
    backup_filename = f"backup_leetcode_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
    if os.path.exists(filename):
        os.rename(filename, backup_filename)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def scroll_to_bottom():
    """Scrolls to the bottom of the page to load all dynamically loaded content."""
    last_height = CODE_DRIVER.execute_script("return document.body.scrollHeight")
    while True:
        CODE_DRIVER.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = CODE_DRIVER.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def scrape_code(problem_url):
    """Scrapes the accepted solution code from the problem's submissions page."""
    wait = WebDriverWait(CODE_DRIVER, 15)
    CODE_DRIVER.get(problem_url + "/submissions/")
    time.sleep(TIME_DELAY)

    try:
        solved_dropdown = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Accepted")))
        solved_dropdown.click()
        scroll_to_bottom()
        time.sleep(2)

        code_elements = CODE_DRIVER.find_elements(By.CLASS_NAME, "ace_line_group")
        code = "\n".join([elem.text for elem in code_elements if elem.text])
        return code.strip() if code else None

    except Exception as e:
        print(f"Error scraping {problem_url}: {e}")
        return None

def sign_into_leetcode_google():
    """Automates LeetCode login using Google."""
    # Logging out first can help clear any previous session state
    CODE_DRIVER.get("https://leetcode.com/accounts/logout")
    CODE_DRIVER.get("https://leetcode.com/accounts/google/login/")
    wait = WebDriverWait(CODE_DRIVER, 30)
    try:
        # Wait for the email input field and enter email
        email = input("Enter your Google email: ")
        email_input = wait.until(EC.presence_of_element_located((By.NAME, "identifier")))
        email_input.click()  # Ensure the field is selected
        time.sleep(1)  # Short delay
        email_input.send_keys(email)
        wait.until(EC.element_to_be_clickable((By.ID, "identifierNext"))).click()
        # Wait for the password field to appear
        password = input("Enter your Google password: ")
        password_input = wait.until(EC.presence_of_element_located((By.NAME, "Passwd")))
        time.sleep(2)  # Ensure password field is fully ready
        password_input.click()
        password_input.send_keys(password)
        wait.until(EC.element_to_be_clickable((By.ID, "passwordNext"))).click()

        # Pause for potential CAPTCHA or 2FA challenges
        time.sleep(15)
        print("Google login successful!")
    except Exception as e:
        print("Google login failed:", e)


def fetch_problem_details(problem_url):
    """Fetches the problem description and solution from a given LeetCode problem page."""
    try:
        # Open problem page
        CODE_DRIVER.get(problem_url + "description/")
        wait = WebDriverWait(CODE_DRIVER, 15)

        try:
            time.sleep(2)  # Allow time for the content to load
            description_div = CODE_DRIVER.find_element(By.XPATH,
                                                       "/html/body/div[1]/div[2]/div/div/div[4]/div/div/div[4]")
            description_html = description_div.get_attribute("outerHTML")

            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(description_html, 'html.parser')

            # Extract the text and image links
            problem_description = soup.get_text(separator="\n").strip()  # Extracting text
            images = soup.find_all('img')  # Finding all images in the description

            # Process images: get their URLs and replace image elements in the text
            for img in images:
                img_url = img.get('src')
                if img_url:
                    print(f"Found image URL: {img_url}")  # Debugging: print the image URL
                    # Replace the image with its URL in the text
                    img['src'] = img_url
                    problem_description = problem_description.replace(str(img), img_url)

            print("Problem Description:\n", problem_description)  # Debugging output



        except Exception as e:
            print(f"⚠️ Unable to extract description: {e}")
            problem_description = "Description not extracted yet"

        try:

            click_element = WebDriverWait(CODE_DRIVER, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "/html/body/div[1]/div[2]/div/div/div[4]/div/div/div[1]/div[1]/div[1]/div/div[5]"))
            )
            click_element.click()  # Click the element

            print("Clicked the specified element.")
            time.sleep(3)

            solution_div = WebDriverWait(CODE_DRIVER, 15).until(
                EC.element_to_be_clickable((By.XPATH,
                                            "/html/body/div[1]/div[2]/div/div/div[4]/div/div/div[6]/div/div/div[3]/div[3]/div[1]/div[2]"))
            )
            solution_div.click()  # Click the first solution div
            time.sleep(2)  # Wait for the solution to load
            print("Solution here")
            # Extract solution text
            solution_div_text = CODE_DRIVER.find_element(By.XPATH,
                                                         "/html/body/div[1]/div[2]/div/div/div[4]/div/div/div[6]/div[2]/div/div/div/div[2]/div/div[1]/div[2]")
            code_elements = solution_div_text.find_elements(By.TAG_NAME, 'code')
            solution_text =""
            # Parse HTML with BeautifulSoup to get clean text
            code_snippets = [element.text for element in code_elements]
            if code_snippets:
                for i, code in enumerate(code_snippets):
                   solution_text +=f"Code Snippet {i + 1}:\n{code}\n---"




        except Exception as e:
            print(f"⚠️ Unable to extract solution: {e}")
            solution_text = "Solution not extracted yet"

        return problem_description, solution_text

    except Exception as e:
        print(f"⚠️ Error fetching details from {problem_url}: {e}")
        return "Description not found", "Solution not found"


def scrape_problems():
    """Scrapes LeetCode problems and accepted solutions, then saves them in a JSON file."""
    make_directory("./leet_code_solutions")
    CODE_DRIVER.get("https://leetcode.com/problemset/")
    wait = WebDriverWait(CODE_DRIVER, 15)
    problems_data = {"problems": []}

    while True:
        time.sleep(TIME_DELAY)
        scroll_to_bottom()  # Ensure all questions are loaded

        try:
            row_groups_css_selector = '#__next > div.flex.min-h-screen.min-w-\[360px\].flex-col.text-label-1.dark\:text-dark-label-1 > div.mx-auto.w-full.grow.p-4.md\:max-w-\[888px\].md\:p-6.lg\:max-w-screen-xl.dark\:bg-dark-layer-bg.bg-white > div.grid.grid-cols-4.gap-4.md\:grid-cols-3.lg\:grid-cols-4.lg\:gap-6 > div.col-span-4.md\:col-span-2.lg\:col-span-3 > div:nth-child(4) > div.-mx-4.transition-opacity.md\:mx-0 > div > div > div:nth-child(2)'
            row_group = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, row_groups_css_selector)))

            rows = row_group.find_elements(By.XPATH, "./div")  # Each row represents a problem

            for row in rows:
                try:
                    title_element = row.find_element(By.XPATH, './/a[contains(@href, "/problems/")]')
                    title = title_element.text.strip()
                    problem_url =  title_element.get_attribute("href")

                    # ✅ Improved Difficulty Extraction
                    difficulty_element = row.find_element(By.XPATH,
                                                          './/span[contains(text(), "Easy") or contains(text(), "Medium") or contains(text(), "Hard")]')
                    difficulty = difficulty_element.text.strip() if difficulty_element else "Unknown"

                    accuracy_element = row.find_element(By.XPATH, './/div[@role="cell"][5]/span')
                    accuracy = accuracy_element.text.strip() if accuracy_element else "Unknown"

                    solution_link_elements = row.find_elements(By.XPATH, './/a[@aria-label="solution"]')
                    solution_url = "https://leetcode.com" + solution_link_elements[0].get_attribute(
                        "href") if solution_link_elements else None

                    problems_data["problems"].append({
                        "title": title,
                        "difficulty": difficulty,
                        "accuracy": accuracy,
                        "problem_url": problem_url,
                        "solution_url": solution_url
                    })

                    print(f"✅ Scraped: {title} - {difficulty} - {accuracy} - {problem_url}")
                #     redirect to problem_url

                except Exception as e:
                    print("⚠️ Error extracting problem details:", e)

        except Exception as e:
            print("⚠️ Error loading problems:", e)

        # # ✅ Updated Pagination Handling
        # try:
        #     next_button = wait.until(EC.presence_of_element_located((By.XPATH, '//button[@aria-label="next"]')))
        #     if "bg-fill-3" in next_button.get_attribute("class"):  # Active button class
        #         next_button.click()
        #         time.sleep(3)  # Allow time for new data to load
        #     else:
        #         break  # No more pages left
        # except Exception as e:
        #     print("⚠️ No next button found or pagination error:", e)
        #     break
        break
    save_json(problems_data)
    print("🎉 Scraping completed! Data saved.")

if __name__ == "__main__":
    # sign_into_leetcode_google()
    # scrape_problems()
    fetch_problem_details("https://leetcode.com/problems/merge-two-sorted-lists/")
    CODE_DRIVER.quit()
