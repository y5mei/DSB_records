from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import argparse


def random_sleep(min_seconds=1, max_seconds=5):
    """
    Pauses execution for a random duration between min_seconds and max_seconds.
    This randomness is very important, without it, OAuth will easily detect the request is from a bot,
    and block the access.

    Args:
        min_seconds: Minimum sleep duration (seconds).
        max_seconds: Maximum sleep duration (seconds).
    """
    sleep_duration = random.uniform(min_seconds, max_seconds)
    time.sleep(sleep_duration)
    return sleep_duration

def record_download_url(date_str):
    year = date_str[:4]  # Extract the year from the date string
    url = f"https://prod.anna-dsb.com/file-download/Records/OTC-Products/Delta/UPI/{year}/{date_str}/Equity/"
    return url

def record_csv_file_name(date_str):
    return f"Equity-{date_str}.records"

def login_and_download(url, email, password, date_str):
    driver = None  # initialize driver to none.
    try:
        # 1. Click the login button to go to the login page.
        try:
            driver = webdriver.Chrome()
            driver.get(url)

            login_button = WebDriverWait(driver, 10, random_sleep(1,2)).until(
                EC.element_to_be_clickable((By.ID, "auth0-login-button"))
            )
            random_sleep(2,3)
            login_button.click()

            WebDriverWait(driver, timeout=30, poll_frequency=5).until(
                lambda driver: driver.current_url.startswith("https://auth.anna-dsb.com/login")
                               or (print(f"Current URL: {driver.current_url}, waiting for the login button to be clicked, you can also do it manually...") or False)  # prints, and returns false.
            )
        except Exception as e:
            print(f"Login failed: {e}")

        # 2. Input the login email and password
        try:
            # Wait for at least one element to be present
            WebDriverWait(driver, 30, poll_frequency=random_sleep(1,2)).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))  # wait for the body.
            )
        except Exception as e:
            print(f"Error loading login page body: {e}")

        # type in email
        try:
            email_input = WebDriverWait(driver, 10, poll_frequency=random_sleep(1,2)).until(
                EC.presence_of_element_located((By.ID, "1-email"))
            )
            email_input.clear()
            email_input.send_keys(email)
            print("Email field filled successfully")
        except Exception as e:
            print(f"Error filling email field: {e}")

        # type in password
        try:
            password_input = WebDriverWait(driver, 10, poll_frequency=random_sleep(2,3)).until(
                EC.presence_of_element_located((By.XPATH, "//input[@name='password']"))
            )
            password_input.clear()
            password_input.send_keys(password)
            print("Password field filled successfully.")
        except Exception as e:
            print(f"Error filling password field: {e}")

        # click continue button to actually login
        try:
            continue_button = WebDriverWait(driver, 20, poll_frequency=random_sleep(1,6)).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.auth0-lock-submit"))
            )
            continue_button.click()
            print("Continue button clicked.")
        except Exception as e:
            print(f"Error clicking continue button on login page: {e}")

        # 3. Go to the webpage url that has the record file.
        try:
            random_sleep(3,8)
            # navigate to the UPI record page, something like https://prod.anna-dsb.com/file-download/Records/OTC-Products/Delta/UPI/2025/20250130/Equity/
            driver.get(record_download_url(date_str))
        except Exception as e:
            print(f"Error navigating to record url {record_download_url(date_str)}: {e}")

        # 4. Download the file.
        try:
            download_link = WebDriverWait(driver, 10, poll_frequency=random_sleep(2, 5)).until(
                EC.element_to_be_clickable((By.LINK_TEXT, record_csv_file_name(date_str)))
            )
            download_link.click()
            random_sleep(10,15)
            print(f"Record file downloaded...")
        except Exception as e:
            print(f"Error downloading record file {record_csv_file_name(date_str)}: {e}")
        return
    except Exception as e:
        print(f"An error occured: {e}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Download Equity records.")
    parser.add_argument("--date", default="20250121", required=True, help="Date string in YYYYMMDD format.")
    parser.add_argument("--email", default="your-email@gmail.com", required=True, help="Email address for login.")
    parser.add_argument("--password", default="your-password", required=True, help="Password for login.")

    args = parser.parse_args()
    date_str = args.date
    email = args.email
    password = args.password

    login_url = "https://prod.anna-dsb.com/"
    print("Going to download ", record_csv_file_name(date_str), " file from this url: ", record_download_url(date_str))
    login_and_download(login_url, email, password, date_str)