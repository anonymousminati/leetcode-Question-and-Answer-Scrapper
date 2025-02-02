import undetected_chromedriver as uc
import json
import time
import os
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

TIME_DELAY = 2

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

def urlify(s):
    """Sanitizes a string to be used as a filename or key."""
    s = re.sub(r"[^\w\s]", '', s)  # Remove non-alphanumeric characters
    return re.sub(r"\s+", '-', s)   # Replace whitespace with dashes

def make_directory(path):
    """Creates a directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)

def save_json(data, filename="leet_code_solutions.json"):
    """Saves the given data to a JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def scrape_code(problem_url):
    """Scrapes the accepted solution code from the problem's submissions page."""
    wait = WebDriverWait(CODE_DRIVER, 15)
    CODE_DRIVER.get(problem_url + "/submissions/")
    CODE_DRIVER.implicitly_wait(TIME_DELAY)
    try:
        # Wait for the "Accepted" link and click it
        solved_dropdown = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Accepted")))
        solved_dropdown.click()
        CODE_DRIVER.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Additional delay to ensure dynamic content loads
        lines = CODE_DRIVER.find_elements(By.CLASS_NAME, "ace_line_group")
        code = "\n".join([line.text for line in lines])
        return code.strip()
    except Exception as e:
        print(f"Error scraping {problem_url}: {e}")
        return ""

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

def scrape_problems():
    """Scrapes LeetCode problems and accepted solutions, then saves them in a JSON file."""
    make_directory("./leet_code_solutions")
    CODE_DRIVER.get("https://leetcode.com/problemset/algorithms/")
    wait = WebDriverWait(CODE_DRIVER, 15)
    problems_data = {"problems": []}
    try:
        # Click to show solved problems (XPath may need updating if LeetCode changes its layout)
        solved_dropdown = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="question-app"]/div/div[2]/div[2]/div/div[2]/div[4]')
        ))
        solved_dropdown.click()

        all_dropdown = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//*[@id="question-app"]/div/div[2]/div[2]/div/div[2]/div[4]/div/div/div/div[2]')
        ))
        all_dropdown.click()

        table = CODE_DRIVER.find_element(By.CLASS_NAME, 'reactable-data')
        problem_links = {}
        for row in table.find_elements(By.TAG_NAME, "tr"):
            try:
                link_elem = row.find_element(By.TAG_NAME, "a")
                title = link_elem.text
                href = link_elem.get_attribute("href")
                if title and href:
                    problem_links[title] = href
            except Exception:
                continue

        for title, href in problem_links.items():
            print(f"Scraping: {title}")
            code = scrape_code(href)
            if code:
                problems_data["problems"].append({
                    "title": title,
                    "url": href,
                    "solutions": {
                        "Python": code
                    }
                })
                print(f"Solution saved for: {title}")
            else:
                print(f"No solution found for: {title}")

        save_json(problems_data)
        print("All data saved to leet_code_solutions.json")
    except Exception as e:
        print("Error in scraping problems:", e)

if __name__ == "__main__":
    sign_into_leetcode_google()
    scrape_problems()
    CODE_DRIVER.quit()
