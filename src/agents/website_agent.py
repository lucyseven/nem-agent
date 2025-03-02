from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# 🔹 Correct Edge WebDriver path
edge_driver_path = r"C:\WebDrivers\msedgedriver.exe"
service = Service(edge_driver_path)

def execute_website_agent(customer_data, account_number):
    """Automate filling out the Annual True-Up Application form."""

    # Start Edge browser
    driver = webdriver.Edge(service=service)
    driver.maximize_window()

    # Open the website
    driver.get("https://sdcommunitypower.org/annual-true-up-application/")
    time.sleep(3)

    # 🔹 Scroll to the section where the iframe is loaded
    driver.execute_script("window.scrollTo(0, 700);")  # Adjust if needed
    time.sleep(2)

    # 🔹 **Wait for the iframe to appear**
    try:
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='forms.monday.com']"))
        )
        print("✅ Found the iframe!")
    except:
        print("❌ Iframe not found!")
        driver.quit()
        return "Failed: Iframe not found."

    # 🔹 **Switch to the iframe**
    driver.switch_to.frame(iframe)
    print("✅ Switched to the iframe!")

    # **Wait for the input fields inside the iframe**
    try:
        name_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "name-input"))
        )
        print("✅ Found Name Field!")
    except:
        print("❌ Name field not found!")
        driver.quit()
        return "Failed: Name field not found."

    # 1️⃣ **Fill in First & Last Name**
    name_field.send_keys(f"{customer_data['first_name']} {customer_data['last_name']}")



    # 2️⃣ **Fill in SDG&E Account Number**
    account_field = driver.find_element(By.ID, "text-input")
    account_field.send_keys(account_number)

    # 3️⃣ **Fill in Service Address**
    address_field = driver.find_element(By.ID, "text1-input")
    address_field.send_keys(customer_data["address"])

    # 4️⃣ **Fill in ZIP Code**
    zip_field = driver.find_element(By.ID, "numbers6-input")
    zip_field.send_keys(customer_data["zip"])

    # 5️⃣ **Fill in City**
    city_field = driver.find_element(By.ID, "text2-input")
    city_field.send_keys(customer_data["city"])

    # 6️⃣ **Click the dropdown to open the country list**
    dropdown_arrow = driver.find_element(By.CSS_SELECTOR, "[data-testid='icon']")
    dropdown_arrow.click()
    time.sleep(2)

    # 6️⃣.1 **Type "1" to filter country codes that start with +1**
    dropdown_input = driver.find_element(By.ID, "react-select-2-input")
    dropdown_input.send_keys("1")
    time.sleep(2)

    # 6️⃣.2 **Scroll until "+1 United States" appears**
    max_scroll_attempts = 20
    scroll_count = 0

    while scroll_count < max_scroll_attempts:
        try:
            us_option = driver.find_element(By.XPATH, "//div[contains(text(), '(+1) United States')]")
            us_option.click()
            break
        except:
            dropdown_input.send_keys(Keys.ARROW_DOWN)
            time.sleep(1)
            scroll_count += 1

    if scroll_count == max_scroll_attempts:
        print("⚠️ Could not find '+1 United States'. Please check dropdown structure.")

    # 7️⃣ **Fill in Phone Number**
    phone_field = driver.find_element(By.ID, "phone-phone-number-input")
    phone_field.send_keys(customer_data["phone"])

    # 8️⃣ **Fill in Email**
    email_field = driver.find_element(By.ID, "email-input")
    email_field.send_keys(customer_data["email"])

    # 9️⃣ **Click the Checkbox (Agree to Terms)**
    checkbox = driver.find_element(By.CSS_SELECTOR, "[data-testid='checkbox-checkbox_check-checkbox']")
    checkbox.click()

    # 🔟 **Click Submit Button**
    submit_button = driver.find_element(By.CSS_SELECTOR, "[data-testid='submit-form-button']")
    submit_button.click()

    # Wait for submission to complete
    time.sleep(5)

    # Close the browser
    #driver.quit()

    return f"✅ Successfully submitted for {customer_data['first_name']} {customer_data['last_name']}!"
