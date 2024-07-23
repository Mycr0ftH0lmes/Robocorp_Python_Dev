from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    open_robot_order_website()
    get_Orders()
    fill_the_form()
    archive_receipts()


def open_robot_order_website():
    browser.goto(url="https://robotsparebinindustries.com/#/robot-order")

def get_Orders():
    http = HTTP()

    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)
    csv_file = Tables()
    robot_orders = csv_file.read_table_from_csv("orders.csv")
    for order in robot_orders:
        fill_the_form(order)

def fill_the_form(order):
    page = browser.page()

    head_names = {
        "1" : "Roll-a-thor head",
        "2" : "Peanut crusher head",
        "3" : "D.A.V.E head",
        "4" : "Andy Roid head",
        "5" : "Spanner mate head",
        "6" : "Drillbit 2000 head"
    }
    head_number = order["Head"]
    page.select_option("#head", head_names.get(head_number))
    page.select_option(".radio form-check", order["Body"])
    page.fill(".form-control", order["Legs"])
    page.fill("#address", order["Address"])
    while True:
        page.click("#order")
        order_another = page.query_selector("#order-another")
        if order_another:
            pdf_path = store_receipt_as_pdf(int(order["Order number"]))
            screenshot_path = screenshot_robot(int(order["Order number"]))
            embed_screenshot_to_receipt(screenshot_path, pdf_path)


def screenshot_robot(order_number):
    try:
        page = browser.page()

        screenshot_path = f"output/screenshots/{order_number}.png"
        robot_image = page.locator("#robot-preview-image")
        if robot_image.exists():
            robot_image.screenshot(path=screenshot_path)
            return screenshot_path
        else:
            print(f"Error: Robot image not found for order {order_number}.")
            return None
    except Exception as e:
        print(f"Error taking screenshot: {str(e)}")
        return None
    
def embed_screenshot_to_receipt(screenshot_path, pdf_path):
    try:
        pdf = PDF()

        pdf.add_watermark_image_to_pdf(image_path=screenshot_path, source_path=pdf_path, output_path=pdf_path)
        print(f"Screenshot embedded in {pdf_path}")
    except Exception as e:
        print(f"Error embedding screenshot: {str(e)}")

def store_receipt_as_pdf(order_number):
    try:
        page = browser.page()
        
        receipt_element = page.locator("#receipt")
        if receipt_element.exists():
            order_html = receipt_element.inner_html()
            pdf = PDF()
            pdf_path = f"output/receipts/{order_number}.pdf"
            pdf.html_to_pdf(order_html, pdf_path)
            return pdf_path
        else:
            print(f"Error: Receipt element not found for order {order_number}.")
            return None
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        return None

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip("./output/receipts", "./output/receipts.zip")