import os
import datetime
import pandas as pd
from httpx import Client
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.settings import ModelSettings
from openai import AsyncAzureOpenAI
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.exceptions import UnexpectedModelBehavior
from dotenv import load_dotenv
import json
import datetime
import pandas as pd
import os


load_dotenv()
OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
API_VERSION = os.getenv("API_VERSION")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")
azure_client = AsyncAzureOpenAI(
    azure_endpoint=OPENAI_ENDPOINT,
    api_key=OPENAI_API_KEY,
    api_version=API_VERSION
)

model = OpenAIChatModel(
    OPENAI_MODEL,
    provider=OpenAIProvider(openai_client=azure_client),
)
 
class Product(BaseModel):
    brand_name: str = Field(title='Brand Name', description="The brand name of the product")
    product_name: str = Field(title='Product Name', description="The name of the product")
    price : float = Field(title='Price', description="The price of the product")
    rating_count: int = Field(title='Rating Count', description="The number of ratings the product has received")
 
class Results(BaseModel):
    dataset: list[Product] = Field(title='Dataset', description="List of products")
 
web_scraping_agent = Agent[None, Results](
    name='web_scraping_agent',
    model=model,
    system_prompt=("""You are a web scraping agent that extracts product information from e-commerce web pages.
        
        Your task is to:
        1. Use the fetch_html_text() function to get HTML content from the provided URL
        2. Extract product information from the HTML and return it in the exact JSON structure specified
        
        You MUST return the data in this exact JSON format:
        {
            "dataset": [
                {
                    "brand_name": "string",
                    "product_name": "string", 
                    "price": float,
                    "rating_count": integer
                }
            ]
        }
        
        Extract all available products from the page. If a field is missing, use reasonable defaults:
        - brand_name: "Unknown" if not found
        - product_name: use the product title/name
        - price: 0.0 if not found or not parseable
        - rating_count: 0 if not found
        
        Return only valid JSON in the specified structure.
        """),
     retries=2,
     model_settings=ModelSettings(
        max_tokens=8000,
        temperature=0.1
        ),
)
 
 
@web_scraping_agent.tool_plain(retries=1)   # You can use tools parameter also to create an agent with tools
def fetch_html_text(url: str) -> str:
    """Fetch HTML text from a given URL.
     Args:
         url (str): The URL of the web page to fetch.
 
     Returns:
         str: The HTML text from the given URL.
     """
    print("Fetching HTML text from URL:", url)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Accept-Language": "en-US,en;q=0.9",
    }
 
    with Client(headers=headers) as client:
        response = client.get(url, timeout=20)
        if response.status_code != 200:
            return f'"Error: Unable to fetch the URL. Status code: {response.status_code}"'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        with open('soup.txt', 'w', encoding='utf-8') as f:
            f.write(soup.get_text())
        print('Soup file saved')
        return soup.get_text().replace('\n', ' ').replace('\r', ' ')
    
 
def main(URL) -> None:
    
    try:
        response = web_scraping_agent.run_sync(URL)
        
        json_output = response.output
        try:
            if json_output.startswith('```json'):
                # Remove markdown code block markers
                json_output = json_output.replace('```json', '').replace('```', '').strip()
            
            parsed_data = json.loads(json_output)
            result_data = Results(**parsed_data)
            print(f"Successfully parsed data with {len(result_data.dataset)} products")
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error parsing JSON: {e}")
            return None
            
        print('='*50)
        print("Input_tokens:", response.usage().input_tokens)
        print("Output_tokens:", response.usage().output_tokens) 
        print("Total_tokens:", response.usage().total_tokens)
 
        lst = []
        for item in result_data.dataset:
            lst.append(item.model_dump())
 
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        df = pd.DataFrame(lst)
        df.to_csv(f'web_scraping_results_{timestamp}.csv', index=False)
        print(f"Results saved to web_scraping_results_{timestamp}.csv")
        print(f"Successfully extracted {len(lst)} products!")
    except UnexpectedModelBehavior as e:
        print(f"An error occurred: {e}")
 
if __name__ == "__main__":
    URL = "https://www.ikea.com/in/en/cat/beds-bm003/"
    main(URL)