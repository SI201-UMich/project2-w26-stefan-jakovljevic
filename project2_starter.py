# SI 201 HW4 (Library Checkout System)
# Your name: Stefan Jakovljevic
# Your student id: 35306972
# Your email: jakovlje@umich.edu
# Who or what you worked with on this homework (including generative AI like ChatGPT):
# If you worked with generative AI also add a statement for how you used it.
# e.g.:
# Asked ChatGPT for hints on debugging and for suggestions on overall code structure
#
# I did not use ChatGPT or any GenAI for this assignment.
#
# Did your use of GenAI on this assignment align with your goals and guidelines in your Gen AI contract? If not, why?
#
# Yes, it does. I told myself I was not going to use it.
#
# --- ARGUMENTS & EXPECTED RETURN VALUES PROVIDED --- #
# --- SEE INSTRUCTIONS FOR FULL DETAILS ON METHOD IMPLEMENTATION --- #

from bs4 import BeautifulSoup
import re
import os
import csv
import unittest
import requests  # kept for extra credit parity


# IMPORTANT NOTE:
"""
If you are getting "encoding errors" while trying to open, read, or write from a file, add the following argument to any of your open() functions:
    encoding="utf-8-sig"
"""


def load_listing_results(html_path) -> list[tuple]:
    """
    Load file data from html_path and parse through it to find listing titles and listing ids.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples containing (listing_title, listing_id)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    listt = []
    f = open(html_path, encoding="utf-8-sig")
    html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    listing_title_arr = soup.find_all("div", {"class": "t1jojoys dir dir-ltr"})
    for listing in listing_title_arr:
        id = listing.get("id", None)
        if id:
            id = id[6:]
        listt.append((listing.text, id))
    f.close()
    return listt
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def get_listing_details(listing_id) -> dict:
    """
    Parse through listing_<id>.html to extract listing details.

    Args:
        listing_id (str): The listing id of the Airbnb listing

    Returns:
        dict: Nested dictionary in the format:
        {
            "<listing_id>": {
                "policy_number": str,
                "host_type": str,
                "host_name": str,
                "room_type": str,
                "location_rating": float
            }
        }
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    d = {}
    html = ""
    with open(os.path.join("html_files", f"listing_{listing_id}.html"), encoding="utf-8-sig") as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    # policy number
    policy_number = soup.find("li", {"class": "f19phm7j dir dir-ltr"})
    policy_number = policy_number.find_all("span")[0].text
    # host type
    host_type = "Superhost" if len(soup.find_all("span", {"class": "_1mhorg9"})) > 0 else "regular"
    # host name
    host_div = soup.find_all("div", {"class": "tehcqxo dir dir-ltr"})[0]
    host_name = host_div.find_all("h2", {"class" : "hnwb2pb dir dir-ltr"})[0]
    host_name = host_name.text if host_name else None
    match = re.findall("Hosted by (.+)", host_name)
    if match:
        host_name = match[0]
    # room type
    room_type_div = soup.find("h2", {"class": "_14i3z6h"})
    room_type_text = room_type_div.text if room_type_div else ""

    text = room_type_text.lower()

    if "private" in text:
        room_type = "Private Room"
    elif "shared" in text:
        room_type = "Shared Room"
    else:
        room_type = "Entire Room"
    # location rating
    location_rating = 0.0
    try:
        location_div = soup.find_all("span", {"class": "_4oybiu"})[3]
        location_rating = float(location_div.text)
    except:
        location_rating = 0.0

    d[listing_id] = {
        "policy_number": policy_number,
        "host_type": host_type,
        "host_name": host_name,
        "room_type": room_type,
        "location_rating": round(location_rating, 1)
    }

    # print(policy_number, host_type, host_name, room_type, location_rating)
    return d
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def create_listing_database(html_path) -> list[tuple]:
    """
    Use prior functions to gather all necessary information and create a database of listings.

    Args:
        html_path (str): The path to the HTML file containing the search results

    Returns:
        list[tuple]: A list of tuples. Each tuple contains:
        (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    results = []
    listings = load_listing_results(html_path)

    for title, listing_id in listings:
        details_dict = get_listing_details(listing_id)
        details = details_dict.get(listing_id, {})
        results.append((
            title,
            listing_id,
            details.get("policy_number"),
            details.get("host_type"),
            details.get("host_name"),
            details.get("room_type"),
            details.get("location_rating")
        ))

    return results
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def output_csv(data, filename) -> None:
    """
    Write data to a CSV file with the provided filename.

    Sort by Location Rating (descending).

    Args:
        data (list[tuple]): A list of tuples containing listing information
        filename (str): The name of the CSV file to be created and saved to

    Returns:
        None
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    sorted_data = sorted(data, key=lambda x: x[6], reverse=True)

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # header
        writer.writerow([
            "Listing Title",
            "Listing ID",
            "Policy Number",
            "Host Type",
            "Host Name",
            "Room Type",
            "Location Rating"
        ])
        for row in sorted_data:
            writer.writerow(row)
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def avg_location_rating_by_room_type(data) -> dict:
    """
    Calculate the average location_rating for each room_type.

    Excludes rows where location_rating == 0.0 (meaning the rating
    could not be found in the HTML).

    Args:
        data (list[tuple]): The list returned by create_listing_database()

    Returns:
        dict: {room_type: average_location_rating}
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    totals = {}
    counts = {}
    for row in data:
        room_type = row[5]
        rating = row[6]
        if rating == 0.0:
            continue
        if room_type not in totals:
            totals[room_type] = 0.0
            counts[room_type] = 0
        totals[room_type] += rating
        counts[room_type] += 1
    d = {}
    for room_type in totals:
        d[room_type] = totals[room_type] / counts[room_type]

    return d
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


def validate_policy_numbers(data) -> list[str]:
    """
    Validate policy_number format for each listing in data.
    Ignore "Pending" and "Exempt" listings.

    Args:
        data (list[tuple]): A list of tuples returned by create_listing_database()

    Returns:
        list[str]: A list of listing_id values whose policy numbers do NOT match the valid format
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    invalid_ids = []
    for row in data:
        listing_id = row[1]
        policy_number = row[2]
        if policy_number in ("Pending", "Exempt", "pending", "exempt"):
            continue
        if not re.match(r"^(20\d{2}-\d{6}STR|STR-\d{7})$", policy_number):
            invalid_ids.append(listing_id)
    return invalid_ids
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


# EXTRA CREDIT
def google_scholar_searcher(query):
    """
    EXTRA CREDIT

    Args:
        query (str): The search query to be used on Google Scholar
    Returns:
        List of titles on the first page (list)
    """
    # TODO: Implement checkout logic following the instructions
    # ==============================
    # YOUR CODE STARTS HERE
    # ==============================
    pass
    # ==============================
    # YOUR CODE ENDS HERE
    # ==============================


class TestCases(unittest.TestCase):
    def setUp(self):
        self.base_dir = os.path.abspath(os.path.dirname(__file__))
        self.search_results_path = os.path.join(self.base_dir, "html_files", "search_results.html")

        self.listings = load_listing_results(self.search_results_path)
        self.detailed_data = create_listing_database(self.search_results_path)

    def test_load_listing_results(self):
        # TODO: Check that the number of listings extracted is 18.
        # TODO: Check that the FIRST (title, id) tuple is  ("Loft in Mission District", "1944564").
        listings = load_listing_results("html_files/search_results.html")
        self.assertEqual(len(listings), 18)
        self.assertEqual(listings[0], ("Loft in Mission District", "1944564"))

    def test_get_listing_details(self):
        html_list = ["467507", "1550913", "1944564", "4614763", "6092596"]

        # TODO: Call get_listing_details() on each listing id above and save results in a list.
        results = []
        for listing in html_list:
            results.append(get_listing_details(listing))

        # TODO: Spot-check a few known values by opening the corresponding listing_<id>.html files.
        # 1) Check that listing 467507 has the correct policy number "STR-0005349".
        self.assertEqual(results[0]["467507"]["policy_number"], "STR-0005349")
        # 2) Check that listing 1944564 has the correct host type "Superhost" and room type "Entire Room".
        self.assertEqual(results[2]["1944564"]["host_type"], "Superhost")
        self.assertEqual(results[2]["1944564"]["room_type"], "Entire Room")
        # 3) Check that listing 1944564 has the correct location rating 4.9.
        self.assertAlmostEqual(results[2]["1944564"]["location_rating"], 4.9, delta=0.01)

    def test_create_listing_database(self):
        # TODO: Check that each tuple in detailed_data has exactly 7 elements:
        # (listing_title, listing_id, policy_number, host_type, host_name, room_type, location_rating)
        for listing in self.detailed_data:
            self.assertEqual(len(listing), 7)

        # TODO: Spot-check the LAST tuple is ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8).
        self.assertEqual(self.detailed_data[-1], ("Guest suite in Mission District", "467507", "STR-0005349", "Superhost", "Jennifer", "Entire Room", 4.8))


    def test_output_csv(self):
        out_path = os.path.join(self.base_dir, "test.csv")

        # TODO: Call output_csv() to write the detailed_data to a CSV file.
        output_csv(self.detailed_data, out_path)
        # TODO: Read the CSV back in and store rows in a list.
        with open(out_path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
        first_row = rows[1]
        first_row[6] = str(float(first_row[6]))
        self.assertEqual(first_row, ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"])
        # TODO: Check that the first data row matches ["Guesthouse in San Francisco", "49591060", "STR-0000253", "Superhost", "Ingrid", "Entire Room", "5.0"].

        os.remove(out_path)

    def test_avg_location_rating_by_room_type(self):
        # TODO: Call avg_location_rating_by_room_type() and save the output.
        # TODO: Check that the average for "Private Room" is 4.9.
        ratings = avg_location_rating_by_room_type(self.detailed_data)
        self.assertAlmostEqual(ratings.get("Private Room", 0), 4.9, delta=0.01)

    def test_validate_policy_numbers(self):
        # TODO: Call validate_policy_numbers() on detailed_data and save the result into a variable invalid_listings.
        # TODO: Check that the list contains exactly "16204265" for this dataset.
        invalid = validate_policy_numbers(self.detailed_data)
        self.assertEqual(invalid, ["16204265"])


def main():
    detailed_data = create_listing_database(os.path.join("html_files", "search_results.html"))
    output_csv(detailed_data, "airbnb_dataset.csv")


if __name__ == "__main__":
    main()
    unittest.main(verbosity=2)
