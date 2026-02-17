import time
import random
import string
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
    # User requested Institute Card click
    "institute_card": [
         # User provided XPath
        (By.XPATH, "/html/body/div[2]/div/div/main/div/div[2]/button[3]/div/span"),
        # Fallbacks
        (By.XPATH, "/html/body/div[2]/div/div/main/div/div[2]/button[3]/span/svg"),
        (By.XPATH, "//button[contains(., 'Institute')]//svg"),
        (By.XPATH, "//div[contains(text(), 'Institute')]//following::svg[1]"),
        (By.XPATH, "//button[contains(., 'Institute')]"),
    ],
    "list_course_button": [
        (By.XPATH, "//button[contains(., 'List a Course')]"),
        (By.XPATH, "//span[contains(., 'List a Course')]"),
        (By.XPATH, "//div[contains(., 'List a Course')]"),
        (By.XPATH, "//*[text()='List a Course']"),
    ],
    "submit_course_button": [
        (By.XPATH, "//button[contains(text(), 'Submit')]"),
        (By.XPATH, "//button[contains(text(), 'Save')]"),
        (By.XPATH, "//button[contains(text(), 'Create')]"),
        (By.XPATH, "//button[contains(text(), 'Next')]"),
        (By.XPATH, "//div[contains(text(), 'Submit')]"),
        (By.XPATH, "//span[contains(text(), 'Submit')]"),
    ],
    "course_title_dropdown": [
        (By.XPATH, "//label[contains(., 'Course Title')]/following::button[1]"),
        (By.XPATH, "//label[contains(., 'Name')]/following::button[1]"),
        (By.XPATH, "//div[contains(text(), 'Select Course')]"),
    ],
    "affiliation_dropdown": [
        (By.XPATH, "//label[contains(., 'Affiliation')]/following::button[1]"),
        (By.XPATH, "//label[contains(., 'University')]/following::button[1]"),
        (By.XPATH, "//div[contains(text(), 'Select Affiliation')]"),
        (By.XPATH, "//div[contains(text(), 'Submit')]"),
        (By.XPATH, "//span[contains(text(), 'Submit')]"),
    ],
    "intake_dropdown": [
        (By.XPATH, "//label[contains(., 'Intake')]/following::button[1]"),
        (By.XPATH, "//label[contains(., 'Intake')]/following::div[contains(@role, 'combobox')][1]"),
        (By.XPATH, "//div[contains(text(), 'Select Intake')]"),
        (By.XPATH, "//div[contains(text(), 'Intake')]/following::button[1]"),
        (By.XPATH, "//*[text()='Intake']/../following-sibling::div//button"),
    ],
    "min_education_dropdown": [
        (By.XPATH, "//label[contains(., 'Minimum Education')]/following::button[1]"),
        (By.XPATH, "//label[contains(., 'Education')]/following::button[1]"),
        (By.XPATH, "//div[contains(text(), 'Select Education')]"),
    ],
    "brochure_upload": [
        (By.CSS_SELECTOR, "input[type='file']"),
        (By.XPATH, "//input[@accept='.pdf,.doc,.docx']"),
        (By.XPATH, "//label[contains(., 'Brochure')]//input"),
    ],
    "preview_post_button": [
        (By.XPATH, "//button[contains(text(), 'Preview & Post')]"),
        (By.XPATH, "//button[contains(., 'Preview') and contains(., 'Post')]"),
        (By.XPATH, "//span[contains(text(), 'Preview & Post')]"),
    ],

    "save_draft_button": [
        (By.XPATH, "/html/body/div[2]/div/div[1]/div/button/p"),
        (By.XPATH, "//button[contains(., 'Save Draft')]"),
        (By.XPATH, "//p[contains(text(), 'Save Draft')]"),
        (By.XPATH, "//div[contains(text(), 'Save Draft')]"),
        (By.XPATH, "//span[contains(text(), 'Save Draft')]"),
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

def select_dropdown_option(driver, btn_selector, option_text=None, element_name="Dropdown"):
    """
    Clicks a dropdown button and selects an option. If option_text is None, selects a random option.
    """
    print(f"Interacting with {element_name}...")
    try:
        btn = find_element_robust(driver, btn_selector, element_name)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        time.sleep(1)
        try:
            btn.click()
        except:
            driver.execute_script("arguments[0].click();", btn)
        
        time.sleep(1)
        
        # Check body for options (User hint: /html/body)
        # Standard Selectors for Radix UI, Shadcn, MUI, AntD, etc.
        option_xpath = (
            "//*[contains(@role, 'option')] | "
            "//div[contains(@class, 'select-item')] | "
            "//li[contains(@class, 'active') or contains(@class, 'option')] | "
            "//div[contains(@class, 'bg-popover')]//div | "
            "/html/body//div[contains(@role, 'option')] | "
            "/html/body/div[contains(@role, 'listbox')]//div |"
            "//div[contains(@class, 'menu')]//div[contains(@class, 'item')]"
        )
        
        # If specific hint is given, prioritize it
        if "body" in str(btn_selector): 
             # Just in case the user meant the button is directly in body (unlikely) or options are there.
             pass

        options = driver.find_elements(By.XPATH, option_xpath)
        
        visible_options = [opt for opt in options if opt.is_displayed()]
        
        if not visible_options:
            print(f"  No visible options found for {element_name}. Dumping page source snippet near button...")
            try:
                # Debugging: Print parent HTML of button to see structure
                parent = btn.find_element(By.XPATH, "./..")
                print(parent.get_attribute('outerHTML')[:500])
            except:
                pass
            return

        if option_text:
            # Select specific
            for opt in visible_options:
                if option_text.lower() in opt.text.lower():
                    opt.click()
                    print(f"  Selected '{opt.text}'")
                    return
            print(f"  Option '{option_text}' not found, selecting random...")
            random.choice(visible_options).click()
        else:
            # Select random
            choice = random.choice(visible_options)
            print(f"  Selected random: '{choice.text}'")
            choice.click()
            
    except Exception as e:
        print(f"  Failed to interact with {element_name}: {e}")

def fill_course_form(driver):
    print("\n--- Filling Course Form (Exhaustive) ---")
    
    # 1. Fill Text Inputs
    print("Scanning for text inputs...")
    try:
        inputs = driver.find_elements(By.CSS_SELECTOR, "input:not([type='hidden']):not([type='checkbox']):not([type='radio'])")
        for i, inp in enumerate(inputs):
            if inp.is_displayed() and inp.is_enabled():
                try:
                    # Skip if already filled
                    if inp.get_attribute("value"):
                       continue
                       
                    field_name = inp.get_attribute("name") or inp.get_attribute("placeholder") or f"Input {i}"
                    val = ""
                    
                    # Logic to generate relevant data based on field attributes
                    name_lower = field_name.lower()
                    
                    # SKIP inputs that should be dropdowns or specific fields handled later
                    if "intake" in name_lower or "education" in name_lower:
                        print(f"  Skipping input '{field_name}' (handled as dropdown)")
                        continue
                    if "title" in name_lower or "course name" in name_lower:
                         # Heuristic: if it looks like a main course title input but we are handling it as dropdown, skip.
                         # But let's check if the user meant 'Course Title' dropdown.
                         print(f"  Skipping input '{field_name}' (handled as dropdown)")
                         continue

                    # User requested NOT to fill Course Type, Speciality, Discipline
                    if "type" in name_lower or "specia" in name_lower or "discipline" in name_lower:
                        print(f"  Skipping input '{field_name}' (User requested exclusion)")
                        continue

                    if "fee" in name_lower or "price" in name_lower or "amount" in name_lower:
                        val = str(random.randint(10000, 500000))
                    elif "duration" in name_lower:
                        val = str(random.randint(3, 24))
                    elif "seat" in name_lower or "vacanc" in name_lower:
                        val = str(random.randint(10, 60))
                    elif "email" in inp.get_attribute("type") or "email" in name_lower:
                         val = f"testcourse{random.randint(100,999)}@example.com"
                    elif "phone" in name_lower or "mobile" in name_lower or "contact" in name_lower or "telephone" in name_lower:
                        val = str(random.randint(7000000000, 9999999999))
                    elif "date" in name_lower: 
                        val = "01-01-2025" # Simple placeholder
                    elif "stipend" in name_lower:
                        val = str(random.randint(5000, 20000))
                    elif "scholarship" in name_lower:
                        val = "Merit-based up to 50%"
                    elif "full name" in name_lower or "fullname" in name_lower:
                        val = "John Doe Director"
                    else:
                        val = "Test Data " + str(random.randint(1, 100))
                    
                    inp.clear()
                    inp.send_keys(val)
                    print(f"  Filled '{field_name}': {val}")
                except Exception as e:
                    print(f"  Failed to fill input {i}: {e}")
    except Exception as e:
        print(f"  Input scanning failed: {e}")

    # 1.5 Handle Specific Dropdowns
    print("Handling specific dropdowns...")
    select_dropdown_option(driver, SELECTORS["course_title_dropdown"], None, "Course Title Dropdown")
    select_dropdown_option(driver, SELECTORS["affiliation_dropdown"], None, "Affiliation Dropdown")
    
    # Ensure Affiliation dropdown is closed by clicking body
    try:
        driver.find_element(By.TAG_NAME, "body").click()
    except:
        pass
    time.sleep(1)

    # Intake moved to END of form filling as per request
    # print("Selecting Intake...")
    # select_dropdown_option(driver, SELECTORS["intake_dropdown"], None, "Intake Dropdown")
    
    select_dropdown_option(driver, SELECTORS["min_education_dropdown"], None, "Minimum Education Dropdown")

    # 1.6 File Upload (Brochure)
    print("Uploading Brochure...")
    try:
        # Use a generic file input selector if specific ones fail, or loop
        file_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
        if file_inputs:
            file_input = file_inputs[0]
            file_path = r"D:\PC DATA\Desktop\Testing Images\PNG Images\1 MB PNG.png"
            file_input.send_keys(file_path)
            print(f"  Uploaded brochure: {file_path}")
        else:
            
            print("  No file input found for brochure.")
    except Exception as e:
        print(f"  Failed to upload brochure: {e}")

    # 2. Fill Text Areas (Description, etc.)

    # 2. Fill Text Areas (Description, etc.)
    print("Scanning for text areas...")
    try:
        textareas = driver.find_elements(By.CSS_SELECTOR, "textarea, .ql-editor")
        for i, ta in enumerate(textareas):
            if ta.is_displayed():
                try:
                    text = "This is a comprehensive course covering all key aspects. " + "".join(random.choices(string.ascii_letters, k=50))
                    if ta.tag_name == 'div': # Rich text editor
                        driver.execute_script("arguments[0].innerHTML = arguments[1];", ta, f"<p>{text}</p>")
                    else:
                        ta.send_keys(text)
                    print(f"  Filled TextArea {i}")
                except Exception as e:
                    print(f"  Failed to fill TextArea {i}: {e}")
    except Exception as e:
        print(f"  TextArea scanning failed: {e}")

    # 3. Handle Dropdowns (Select elements & Custom Dropdowns)
    print("Scanning for dropdowns...")
    
    # A. Native Selects
    try:
        selects = driver.find_elements(By.TAG_NAME, "select")
        for sel in selects:
            if sel.is_displayed():
                try:
                    options = sel.find_elements(By.TAG_NAME, "option")
                    valid_opts = [o for o in options if o.get_attribute("value")]
                    if valid_opts:
                        random.choice(valid_opts).click()
                        print("  Selected valid option from native dropdown.")
                except:
                    pass
    except:
        pass

    # B. Custom Dropdowns (Buttons or Divs acting as triggers)
    # We look for elements that look like dropdown triggers
    triggers = driver.find_elements(By.XPATH, 
        "//button[contains(@aria-haspopup, 'listbox')] | "
        "//button[contains(@role, 'combobox')] | "
        "//div[contains(@role, 'combobox')] | "
        "//button[contains(., 'Select')] | "
        "//div[contains(text(), 'Select ')]" # Space after Select to avoid matching 'Selection'
    )
    
    print(f"  Found {len(triggers)} potential custom dropdowns.")
    for i, btn in enumerate(triggers):
        if btn.is_displayed() and btn.is_enabled():
            # Check exclusions by button text
            btn_text = btn.text.lower()
            if "type" in btn_text or "specia" in btn_text or "discipline" in btn_text:
                print(f"    Skipping Dropdown {i+1} ('{btn.text}') (User requested exclusion)")
                continue

            try:
                # Check if already has a value (heuristic: implies it might not say 'Select' anymore)
                # But safer to just click and pick another one.
                
                print(f"  Interacting with Dropdown {i+1}...")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                time.sleep(0.5)
                try:
                    btn.click()
                except:
                    driver.execute_script("arguments[0].click();", btn)
                
                time.sleep(1) # Wait for options to appear
                
                
                # Check body for options (User hint: /html/body)
                # Our xpath starts with //* so it covers body. Adding explicit body direct child check just in case.
                option_xpath = (
                    "//*[contains(@role, 'option')] | "
                    "//div[contains(@class, 'select-item')] | "
                    "//li[contains(@class, 'active') or contains(@class, 'option')] | "
                    "//div[contains(@class, 'bg-popover')]//div | "
                    "/html/body//div[contains(@role, 'option')] | "
                    "/html/body/div[contains(@role, 'listbox')]//div"
                )
                
                options = driver.find_elements(By.XPATH, option_xpath)
                visible_opts = [o for o in options if o.is_displayed() and o.text.strip()]
                
                if visible_opts:
                    # Avoid picking placeholders like "Select..."
                    valid_opts = [o for o in visible_opts if "select" not in o.text.lower()]
                    choice = random.choice(valid_opts) if valid_opts else random.choice(visible_opts)
                    
                    print(f"    Selecting '{choice.text}'")
                    try:
                        choice.click()
                    except:
                        driver.execute_script("arguments[0].click();", choice)
                else:
                    print("    No visible options found (might not be a dropdown or failed to open).")
                    
                time.sleep(0.5)
                
            except Exception as e:
                print(f"    Failed to handle Dropdown {i+1}: {e}")

    # LAST STEP: Select Intake as requested
    print("Selecting Intake (Last Step)...")
    # Ensure any previous dropdowns are closed
    try:
        driver.find_element(By.TAG_NAME, "body").click()
    except:
        pass
    time.sleep(1)
    select_dropdown_option(driver, SELECTORS["intake_dropdown"], None, "Intake Dropdown")



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
        
        # 5. Click Institute Card
        institute_card = find_element_robust(driver, SELECTORS["institute_card"], "Institute Card")
        try:
            institute_card.click()
        except:
            driver.execute_script("arguments[0].click();", institute_card)
        print("Clicked Institute Card.")
        
        # 6. Click List a Course Button
        list_course_btn = find_element_robust(driver, SELECTORS["list_course_button"], "List a Course Button")
        try:
            list_course_btn.click()
        except:
            driver.execute_script("arguments[0].click();", list_course_btn)
        print("Clicked List a Course Button.")
        
        # 7. Fill Course Form
        time.sleep(3) # Wait for form
        fill_course_form(driver)
        
        # 8. Submit Form (Preview & Post)
        print("Waiting 4 seconds before submission...")
        time.sleep(4)
        
        submit_btn = find_element_robust(driver, SELECTORS["preview_post_button"], "Preview & Post Button")
        try:
            submit_btn.click()
        except:
            driver.execute_script("arguments[0].click();", submit_btn)
        print("Clicked Preview & Post Button.")

        # 9. Click Save Draft after 3 seconds
        print("Waiting 3 seconds before Save Draft...")
        time.sleep(3)
        
        save_draft_btn = find_element_robust(driver, SELECTORS["save_draft_button"], "Save Draft Button")
        try:
            save_draft_btn.click()
        except:
            driver.execute_script("arguments[0].click();", save_draft_btn)
        print("Clicked Save Draft Button.")

        
        print("Done! Actions completed.")

    except Exception as e:
        print(f"\nERROR: {e}")
    finally:
        input("\nPress Enter to close the browser...")
        driver.quit()

if __name__ == "__main__":
    main()
