import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURATION ---
LOGIN_URL = "https://enterprise.ibns.in/"
EMAIL = "new.enterprise@yopmail.com"
PASSWORD = "Test@123"

# --- SELECTORS ---
# If the script fails to find elements, update these selectors based on the website's HTML.
# You can find these by right-clicking the element in Chrome > Inspect.
SELECTORS = {
    # Try these common ID/Name/Class patterns for Email
    "email": [
        (By.ID, "email"),
        (By.NAME, "email"),
        (By.ID, "username"),
        (By.NAME, "username"),
        (By.CSS_SELECTOR, "input[type='email']"),
        (By.CSS_SELECTOR, "input[type='text']"),
    ],
    # Try these for Password
    "password": [
        (By.ID, "password"),
        (By.NAME, "password"),
        (By.CSS_SELECTOR, "input[type='password']"),
    ],
    # Try these for the Login Button
    "submit_button": [
        (By.CSS_SELECTOR, "button[type='submit']"),
        (By.ID, "login-button"),
        (By.ID, "submit"),
        (By.XPATH, "//button[contains(text(), 'Login')]"),
        (By.XPATH, "//button[contains(text(), 'Sign In')]"),
    ],
    # Try these for the Recruiter Link/Button (SVG Arrow)
    "recruiter_card": [
        (By.CSS_SELECTOR, "body > div.min-h-screen.bg-gray-100 > div > div > main > div > div.grid.sm\:mt-0\.5.gap-4.sm\:grid-cols-2.lg\:grid-cols-3 > button:nth-child(1) > span > svg"),
        (By.CSS_SELECTOR, "svg.lucide-arrow-right"),
        (By.XPATH, "//*[name()='svg'][contains(@class, 'lucide-arrow-right')]"),
        (By.XPATH, "//*[name()='svg'][contains(@class, 'lucide-arrow-right')]/.."), # Parent of the SVG
        (By.XPATH, "//a[normalize-space()='Recruiter']"),
    ],
    # Try these for the Post a Job Button
    "post_job_button": [
        (By.XPATH, "//button[contains(text(), 'Post a Job')]"),
        (By.XPATH, "//a[contains(text(), 'Post a Job')]"),
        (By.XPATH, "//span[contains(text(), 'Post a Job')]"),
        (By.CSS_SELECTOR, "button.post-job"),
    ],
    # --- FORM FIELDS ---
    "job_title": [(By.NAME, "title")],
    "country": [(By.XPATH, "//input[@placeholder='Select Country']")],
    "state": [(By.XPATH, "//input[@placeholder='Select State']")],
    "city": [(By.XPATH, "//input[@placeholder='Select City']")],
    "work_experience_btn": [(By.XPATH, "//button[contains(., 'Select Work Experience')]")],
    "salary_type_btn": [(By.XPATH, "//button[contains(., 'Select Type')]")],
    "min_amount": [(By.NAME, "salary.minAmount")],
    "max_amount": [(By.NAME, "salary.maxAmount")],
    "employment_type_btn": [(By.XPATH, "//button[contains(., 'Select Employment Type')]")],
    "vacancies": [(By.NAME, "noOfVacancy")],
    "education": [(By.XPATH, "//input[@placeholder='Select Preferred Education']")],
    "key_skills": [(By.XPATH, "//input[@placeholder='Select Key Skills']")],
    "job_description": [(By.CSS_SELECTOR, ".ql-editor[data-placeholder='Enter job description here...']")],
    "benefits_editor": [(By.CSS_SELECTOR, ".ql-editor[data-placeholder='Describe here...']")],
    "org_profile": [(By.NAME, "organizationInfo.aboutOrganization")],
    "org_address": [(By.NAME, "organizationInfo.organizationContactAndAddressDetails")],
    "min_experience": [(By.XPATH, "//input[@placeholder='Enter minimum years']")],
    "max_experience": [(By.XPATH, "//input[@placeholder='Enter maximum years']")],
    "save_draft_btn": [(By.XPATH, "//button[text()='Save Draft']")],
    "go_to_dashboard_btn": [
        (By.XPATH, "//a[contains(text(), 'Go to Dashboard')]"),
        (By.XPATH, "//button[contains(text(), 'Go to Dashboard')]"),
        (By.CSS_SELECTOR, "a[href='/en/recruiter/dashboard']"),
    ],
    "job_applicant_menu": [
        (By.XPATH, "//*[@class='w-full text-left py-3 px-4 rounded-md font-medium text-sm transition-all text-gray-700 hover:bg-gray-100 border-l-2 border-borderColor-grayLight rounded-l-none']"),
        (By.CSS_SELECTOR, "a[href*='applicant']"),
        (By.XPATH, "//a[contains(., 'Job Applicant')]"),
        (By.XPATH, "//a[contains(., 'Job Applicants')]"),
        (By.XPATH, "//aside//a[contains(., 'Applicant')]"),
        (By.CSS_SELECTOR, "body > div > div > aside a[href*='applicant']"),
        # Fallbacks
        (By.XPATH, "//div[contains(., 'Job Applicant')]"),
        (By.XPATH, "//span[contains(., 'Job Applicant')]"),
    ],
    "applicant_search_input": [
        # User provided classes - matching distinct ones
        (By.XPATH, "//input[contains(@class, 'pl-12') and contains(@class, 'rounded-full')]"),
        (By.XPATH, "//input[@placeholder='Search']"),
        (By.CSS_SELECTOR, "input[type='search']"),
    ],
}

def find_element_robust(driver, selector_list, element_name):
    """
    Efficiently waits for ANY of the provided selectors to match an element.
    """
    print(f"Looking for {element_name}...")
    
    # Create a list of expected conditions for all selectors
    conditions = [EC.presence_of_element_located((by, val)) for by, val in selector_list]
    
    try:
        # Wait until at least one of the selectors matches
        WebDriverWait(driver, 15).until(EC.any_of(*conditions))
        
        # Now find which one triggered the match
        for by, value in selector_list:
            elements = driver.find_elements(by, value)
            if elements:
                print(f"  Found {element_name} using {by}='{value}'")
                return elements[0]
                
        raise Exception("Wait completed but element not found in list check.")
        
    except Exception as e:
        raise Exception(f"Could not find {element_name}. Timed out.") from e


def select_dropdown_option(driver, btn_selector, option_text, element_name):
    """
    Clicks a dropdown button and selects an option by text.
    """
    print(f"Selecting '{option_text}' from {element_name}...")
    btn = find_element_robust(driver, btn_selector, element_name)
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
    time.sleep(1)
    try:
        btn.click()
    except:
        driver.execute_script("arguments[0].click();", btn)
    
    time.sleep(1)
    try:
        # This covers common dropdown patterns
        option_xpath = f"//*[contains(@role, 'option') or contains(@role, 'listbox')]//*[contains(text(), '{option_text}')] | //*[contains(@class, 'select-content')]//*[contains(text(), '{option_text}')] | //*[text()='{option_text}']"
        option = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, option_xpath))
        )
        option.click()
        print(f"  Selected '{option_text}'")
    except Exception as e:
        print(f"  Failed to select '{option_text}': {e}")

def search_and_select(driver, input_selector, search_text, element_name):
    """
    Types into an input character by character and selects the first matching option.
    """
    print(f"Searching and selecting '{search_text}' in {element_name}...")
    inp = find_element_robust(driver, input_selector, element_name)
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", inp)
    time.sleep(1)
    
    # Clear using keys to ensure events are triggered
    inp.click()
    inp.send_keys(Keys.CONTROL + "a")
    inp.send_keys(Keys.BACKSPACE)
    time.sleep(0.5)
    
    # Type character by character
    for char in search_text:
        inp.send_keys(char)
        time.sleep(0.1)
    
    # time.sleep(3) removed; relying on WebDriverWait below
    
    try:
        # Broader XPath for options, including the specific popover pattern found
        option_xpath = (
            f"//div[contains(@class, 'bg-popover')]//*[contains(text(), '{search_text}')] | "
            f"//*[contains(@role, 'option')]//*[contains(text(), '{search_text}')] | "
            f"//*[contains(@class, 'command-item')]//*[contains(text(), '{search_text}')] | "
            f"//*[contains(text(), '{search_text}') and contains(@class, 'cursor-pointer')] | "
            f"//div[contains(@class, 'select-item')]//*[contains(text(), '{search_text}')]"
        )
        option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, option_xpath))
        )
        try:
            option.click()
        except:
            driver.execute_script("arguments[0].click();", option)
        print(f"  Selected '{search_text}'")
    except Exception as e:
        print(f"  Could not find option for '{search_text}' via click.")
        # Debug: List all visible options
        print("  Available options (debug):")
        options = driver.find_elements(By.XPATH, "//*[contains(@role, 'option')] | //*[contains(@class, 'command-item')] | //*[contains(@class, 'select-item')] | //div[contains(@class, 'bg-popover')]//span")
        for opt in options:
            if opt.text.strip():
                print(f"    - '{opt.text.strip()}'")
        
        print(f"  Trying Enter key as fallback for '{search_text}'...")
        inp.send_keys(Keys.ENTER)
        time.sleep(1)

def fill_job_form(driver):
    print("\n--- Filling All Job Form Fields ---")
    
    # 1. Job Title
    title = find_element_robust(driver, SELECTORS["job_title"], "Job Title")
    title.send_keys("Senior Software Engineer (Automation Test)")
    
    # 2. Location
    search_and_select(driver, SELECTORS["state"], "Goa", "State Input")
    time.sleep(2)
    search_and_select(driver, SELECTORS["city"], "Goa", "City Input")

    # 3. Work Experience
    select_dropdown_option(driver, SELECTORS["work_experience_btn"], "Experienced", "Work Experience Dropdown")
    time.sleep(2)
    
    # Fill Min and Max Experience (0-100, min <= max)
    min_exp = find_element_robust(driver, SELECTORS["min_experience"], "Min Experience")
    min_exp.clear()
    min_exp.send_keys("2")
    
    max_exp = find_element_robust(driver, SELECTORS["max_experience"], "Max Experience")
    max_exp.clear()
    max_exp.send_keys("5")
    
    # 4. Salary
    select_dropdown_option(driver, SELECTORS["salary_type_btn"], "Monthly", "Salary Type Dropdown")
    
    min_sal = find_element_robust(driver, SELECTORS["min_amount"], "Min Salary")
    min_sal.send_keys("50000")
    
    max_sal = find_element_robust(driver, SELECTORS["max_amount"], "Max Salary")
    max_sal.send_keys("80000")
    
    # 5. Employment Type
    select_dropdown_option(driver, SELECTORS["employment_type_btn"], "Full Time", "Employment Type Dropdown")
    
    # 6. Vacancies
    vacancies = find_element_robust(driver, SELECTORS["vacancies"], "Vacancies")
    vacancies.send_keys("5")
    
    # 7. Preferred Education
    search_and_select(driver, SELECTORS["education"], "B.Tech", "Education Input")
    
    # 8. Key Skills
    search_and_select(driver, SELECTORS["key_skills"], "Python", "Skills Input")
    time.sleep(1)
    search_and_select(driver, SELECTORS["key_skills"], "Selenium", "Skills Input")

    # 9. Job Description (200+ characters)
    description_text = (
        "We are looking for a highly skilled Senior Software Engineer to join our dynamic team. "
        "The ideal candidate will have extensive experience in Python, Selenium, and automated testing frameworks. "
        "You will be responsible for designing and implementing robust automation scripts to ensure the quality and reliability of our enterprise platforms. "
        "Strong problem-solving skills and the ability to work collaboratively in an agile environment are essential. "
        "Join us to build the future of healthcare technology!"
    )
    print(f"Entering Job Description ({len(description_text)} chars)...")
    desc_editor = find_element_robust(driver, SELECTORS["job_description"], "Job Description Editor")
    driver.execute_script("arguments[0].innerHTML = arguments[1];", desc_editor, f"<p>{description_text}</p>")
    
    # 10. Benefits (optional)
    benefits_text = (
        "We offer a competitive salary, health insurance, and a flexible work environment. "
        "You will have the opportunity to work with cutting-edge technologies and grow your career in a fast-paced industry. "
        "We also provide regular training and development programs to help you stay ahead in your field."
    )
    print(f"Entering Benefits ({len(benefits_text)} chars)...")
    benefits_editor = find_element_robust(driver, SELECTORS["benefits_editor"], "Benefits Editor")
    driver.execute_script("arguments[0].innerHTML = arguments[1];", benefits_editor, f"<p>{benefits_text}</p>")

    # 11. Organization Info
    org_profile = find_element_robust(driver, SELECTORS["org_profile"], "Org Profile")
    org_profile.send_keys("Leading healthcare technology provider focused on enterprise solutions.")
    
    org_address = find_element_robust(driver, SELECTORS["org_address"], "Org Address")
    org_address.send_keys("123 Health Tech Park, Ahmedabad, Gujarat, India")

    # 12. Save Draft
    print("Clicking Save Draft...")
    save_btn = find_element_robust(driver, SELECTORS["save_draft_btn"], "Save Draft Button")
    try:
        save_btn.click()
    except:
        driver.execute_script("arguments[0].click();", save_btn)
    
    print("Form submitted/saved as draft.")
    time.sleep(5)

def main():
    print("Starting Login Script...")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    try:
        # 1. Navigate to the website
        print(f"Navigating to {LOGIN_URL}...")
        driver.get(LOGIN_URL)
        driver.maximize_window()
        
        # No sleep needed here; find_element_robust will wait for the element to appear
        
        # Check if we need to click a "Login" link
        current_url = driver.current_url
        if "login" not in current_url.lower():
            print("Not on login page yet. Checking for 'Login' link...")
            try:
                login_link = driver.find_element(By.XPATH, "//a[contains(@href, 'login')]")
                login_link.click()
                print("Clicked Login link.")
                time.sleep(3)
            except:
                print("Could not find a 'Login' link.")

        # 2. Enter Email
        email_input = find_element_robust(driver, SELECTORS["email"], "Email Input")
        email_input.clear()
        email_input.send_keys(EMAIL)
        print("Entered email.")
        
        # 3. Enter Password
        password_input = find_element_robust(driver, SELECTORS["password"], "Password Input")
        password_input.clear()
        password_input.send_keys(PASSWORD)
        print("Entered password.")
        
        # 4. Click Login
        submit_btn = find_element_robust(driver, SELECTORS["submit_button"], "Submit Button")
        try:
            submit_btn.click()
        except:
            driver.execute_script("arguments[0].click();", submit_btn)
        print("Clicked Login button.")
        
        # 5. Wait for Login to complete

        # No explicit sleep; we will wait for the recruiter card to appear

        
        # 6. Click Recruiter Card
        recruiter_card = find_element_robust(driver, SELECTORS["recruiter_card"], "Recruiter Card")
        try:
            recruiter_card.click()
        except:
            driver.execute_script("arguments[0].click();", recruiter_card)
        print("Clicked Recruiter Card.")
        
        # time.sleep(3) removed

        
        # 7. Click Post a Job Button
        post_job_btn = find_element_robust(driver, SELECTORS["post_job_button"], "Post a Job Button")
        try:
            post_job_btn.click()
        except:
            driver.execute_script("arguments[0].click();", post_job_btn)
        print("Clicked Post a Job button.")
        

        # time.sleep(5) removed

        fill_job_form(driver)
        
        # 9. Post-Submission Navigation
        print("Waiting for 'Go to Dashboard' button...")
        dashboard_btn = find_element_robust(driver, SELECTORS["go_to_dashboard_btn"], "Go to Dashboard Button")
        try:
            dashboard_btn.click()
        except:
            driver.execute_script("arguments[0].click();", dashboard_btn)
        print("Clicked Go to Dashboard.")
        
        # time.sleep(2) removed; find_element_robust will wait for the menu
        
        print("Navigating to Job Applicants...")
        applicant_menu = find_element_robust(driver, SELECTORS["job_applicant_menu"], "Job Applicant Menu")
        
        # Ensure element is visible and in view
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", applicant_menu)
        time.sleep(1) # Specific short wait for scroll to finish
        
        try:
            WebDriverWait(driver, 5).until(lambda d: applicant_menu.is_displayed() and applicant_menu.is_enabled())
            applicant_menu.click()
        except Exception as e:
             print(f"Standard click failed ({e}), trying JS click...")
             driver.execute_script("arguments[0].click();", applicant_menu)
        print("Clicked Job Applicant.")
        
        # 10. Perform Search
        time.sleep(2) # Wait for applicants page to load
        print("\n--- Performing Applicant Search ---")
        search_input = find_element_robust(driver, SELECTORS["applicant_search_input"], "Applicant Search Input")
        
        # Search for " Deep "
        print("Searching for ' Deep '...")
        search_input.clear()
        search_input.send_keys(" Deep ")
        
        print("Waiting 4 seconds as requested...")
        time.sleep(4)
        
        # Clear and Search for " 8965440003 "
        print("Clearing search and searching for ' 8965440003 '...")
        search_input.send_keys(Keys.CONTROL + "a")
        search_input.send_keys(Keys.BACKSPACE)
        time.sleep(0.5)
        search_input.send_keys(" 8965440003 ")
        
        print("Search sequence complete.")
        time.sleep(2)
        
        print("Done!")

    except Exception as e:
        print(f"\nERROR: {e}")
    finally:
        input("\nPress Enter to close the browser...")
        driver.quit()

if __name__ == "__main__":
    main()
