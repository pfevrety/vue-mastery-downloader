from __future__ import print_function
from vimeo_downloader import Vimeo
from seleniumwire import webdriver
import time
import requests
from lxml import etree
import re
import chalk


### GET COURSES ###


def get_course_urls():
    r = requests.get("https://www.vuemastery.com/sitemap.xml")
    NS = {'s': "http://www.sitemaps.org/schemas/sitemap/0.9"}

    tree = etree.XML(r.content)
    loc_list = tree.xpath("//s:url/s:loc", namespaces=NS)

    course = []
    for loc in loc_list:
        if loc.text.startswith("https://www.vuemastery.com/courses/"):
            course.append({
                "url": loc.text,
                "name": loc.text.split("/")[-1],
                "path": loc.text.split("/")[-2]
            })
    print(chalk.green(f"Found {len(course)} courses"))
    return course


def download_video(url, filename, directory):
    v = Vimeo(url)
    s = v.streams
    s[3].download(download_directory=f'videos/{directory}',
                  filename=filename)


print("Vue Mastery course downloader")
print("==============================")
print("")
email = str(input("Email > "))
password = str(input("Password > "))
print("")
print("")
quality = int(input("Quality (360(1), 480(2), 720(3), 1080(4)) > ")) - 1

print(chalk.red("WARNING: This will download all videos in the course"))
print(chalk.blue("Press enter to continue"))
input()
print(chalk.green("Starting download"))
courses = get_course_urls()

### CREATE CHROME DRIVE INSTANCE ###

brave_path = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"

option = webdriver.ChromeOptions()
option.binary_location = brave_path
option.add_argument("--window-size=1920,1080")


driver = webdriver.Chrome(chrome_options=option)


### LOGIN ###

driver.get("https://www.vuemastery.com/")

time.sleep(2)
login_button = driver.find_element_by_xpath(
    '//*[@id="__layout"]/div/div/div/header/div/nav/div[2]/button[2]')
login_button.click()
print("Login button clicked")
time.sleep(1)


input_email = driver.find_element_by_xpath(
    "//*[@id='__layout']/div/div[2]/div/div[2]/form/div[2]/input")
print("Email input found")

input_password = driver.find_element_by_xpath(
    "//*[@id='__layout']/div/div[2]/div/div[2]/form/div[3]/input")
print("Password input found")
login_button = driver.find_element_by_xpath(
    '//*[@id="__layout"]/div/div[2]/div/div[2]/form/div[5]/button')
print("Login button found")
time.sleep(10)
input_email.send_keys(email)
input_password.send_keys(password)

login_button = driver.find_element_by_xpath(
    '//*[@id="__layout"]/div/div[2]/div/div[2]/form/div[5]/button')
login_button.click()
time.sleep(4)

print(chalk.green("Logged in"))

for i, course in enumerate(courses):
    driver.get(course['url'])
    print(chalk.blue(f"{i}/{len(courses)} - Getting {course['name']}"))
    course_url_video = ''
    for request in driver.requests:
        if request.response:
            if request.url.startswith("https://player.vimeo.com/video/"):
                course_url_video = re.search(
                    "https:\/\/player.vimeo.com\/video\/\d*", request.url).group()
    download_video(course_url_video, f"{i} - {course['name']}", course['path'])
    print(chalk.yellow("Downloaded"))
    time.sleep(2.5)
