
import csv
import requests
from lxml import html


def get_response(company_name: str) -> requests.Response:
    """
    Retrieves html response by sending requests

    Args:
        company_name(str): Company name. This is used as search term in the Google search URL

    Returns:
        requests.Response
    """

    headers = {
      'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,'
                '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
      'accept-language': 'en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
      'dpr': '1',
      'sec-fetch-dest': 'document',
      'sec-fetch-mode': 'navigate',
      'sec-fetch-site': 'none',
      'sec-fetch-user': '?1',
      'upgrade-insecure-requests': '1',
      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }

    search_url = f'https://www.google.com/search?q={company_name}&sourceid=chrome&ie=UTF-8'
    # Retrying 3 times if status code is not 200
    for retry in range(3):
        response = requests.get(search_url, headers=headers)
        if response.status_code == 200:
            return response



def extract_company_details(response: requests.Response) -> dict:
    """
    Extracts company details from HTML response

    Args:
        response(requests.Response): Response object
    
    Returns:
        dict: Extracted company data
    
    """
    parser = html.fromstring(response.text)
    company_name_raw = parser.xpath('//div[contains(@class, "kp-wholepage")]//*[@data-attrid="title"]//text()')
    company_name = company_name_raw[0] if company_name_raw else None
    company_type_raw = parser.xpath('//div[contains(@class, "kp-wholepage")]//div[@data-attrid="subtitle"]//text()')
    company_type = company_type_raw[0] if company_type_raw else None
    website_raw = parser.xpath('//div[contains(@class, "kp-wholepage")]//a[@data-attrid="visit_official_site"]//@href')
    website = website_raw[0] if website_raw else None
    description_raw = parser.xpath('//div[@class="kno-rdesc"]//span/text()')
    description = description_raw[0] if description_raw else None
    stock_price_raw = parser.xpath('//div[@data-attrid="kc:/business/issuer:stock quote"]//text()')
    stock_price = ''.join(stock_price_raw).replace('Stock price:', '').replace('\u202f', '').strip() if stock_price_raw else None
    ceo_raw = parser.xpath('//div[@data-attrid="kc:/organization/organization:ceo"]//a[@class="fl"]//text()')
    ceo = ''.join(ceo_raw).replace('CEO', '').strip() if ceo_raw else None
    founder_raw = parser.xpath('//div[@data-attrid="kc:/business/business_operation:founder"]//text()')
    founder = ''.join(founder_raw).replace('Founders:', '').replace('Founder:','').strip() if founder_raw else None
    founded_raw = parser.xpath('//div[@data-attrid="kc:/organization/organization:founded"]//text()')
    founded = ''.join(founded_raw).replace('Founded:', '').strip() if founded_raw else None
    headquarters_raw = parser.xpath('//div[@data-attrid="kc:/organization/organization:headquarters"]//text()')
    headquarters = ''.join(headquarters_raw).replace('Headquarters:', '').strip() if headquarters_raw else None
    employees_raw = parser.xpath('//div[@data-attrid="ss:/webfacts:number_of_employe"]//text()')
    num_of_employees = ''.join(employees_raw).replace('Number of employees:', '').strip() if employees_raw else None

    company_details = {
      'company_name': company_name,
      'company_type': company_type,
      'website': website,
      'description': description,
      'stock_price': stock_price,
      'ceo': ceo,
      'founder': founder,
      'founded': founded,
      'headquarters': headquarters,
      'number_of_employees': num_of_employees 
    } 
    return company_details


def scrape_data(input_company_names: list, output_file: str):
    """
    Reads list of company names from input file, extracts company data and write to CSV file

    Args:
        input_company_names(list): List of company names
        output_file(str): Output file name
    """
    company_details_list = []
    for company in input_company_names:
        response = get_response(company)
        # If the response fails, even after retries, get_response won't return any response
        if not response:
            print(f'Invalid response for company name {company}')
            continue
        company_details = extract_company_details(response)
        company_details['input_company_name'] = company
        company_details_list.append(company_details)
    write_csv(output_file, company_details_list)

def write_csv(file_name: str, company_details_list: list):
    """
    Writes scraped data to csv file
    
    Args:
        file_name: output file name
        company_details_list: list of scraped company details
    """

    # Writing scraped data to CSV file
    with open(file_name, 'w') as fp:
            fieldnames = company_details_list[0].keys()
            writer = csv.DictWriter(fp, fieldnames=fieldnames)
            writer.writeheader()
            for data in company_details_list:
                writer.writerow(data)


if __name__ == "__main__":

    company_names = ['Amazon', 'Kroger', 'Walgreens', 'Rockstar', 'Ebay']
    output_file_name = 'company_details.csv'
    scrape_data(company_names, output_file_name)
