import base64
import openai
import pandas as pd
import tabulate
from pdf2image import convert_from_path
from PIL import Image
from dotenv import load_dotenv
from IPython.display import display
import json


# Load environment variables
load_dotenv()
OPENAI_API_KEY="sk-open api"

openai.api_key = OPENAI_API_KEY #os.getenv("OPENAI_API_KEY")

# Step 1: Convert PDF to Image
def pdf_to_image(pdf_path, dpi=200, page_num=0):
    pages = convert_from_path(pdf_path, dpi=dpi)
    image = pages[page_num]
    return image

# Step 2: Encode image as base64
def encode_image(image: Image.Image):
    from io import BytesIO
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# Step 3: Send to GPT-4o
def extract_from_image(image: Image.Image, prompt: str):
    base64_image = encode_image(image)

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=500
    )
    return response.choices[0].message.content

def extract_from_pdf(pdf_path,prompt):
    image = pdf_to_image(pdf_path,dpi=200,page_num=0)
    pdf_text = ""
    image = pdf_to_image(pdf_path, dpi=200, page_num=0)
    #display(image.resize((500, 700)))
    output = extract_from_image(image, prompt)
    #print("Extracted Data:\n", output)
    print(type(output))
    cleaned_str = output.strip().removeprefix("```json").removesuffix("```").strip()

# Parse to dictionary
    output = json.loads(cleaned_str)
    print(f"Raw string: {repr(output)}")
    print(type(output))
    return output


def extract_and_append_to_csv(extraction, csv_file="test.csv"):
    # Load the CSV
    df = pd.read_csv(csv_file)
    # Mapping extracted keys to actual CSV column names
    column_map = {
        "total_amount": "Total claim amount (inc VAT)",
        "invoice_date": "Invoice item date",
        "session": "Invoice item description"
    }

    # Prepare a blank row with all columns from the CSV
    new_row = {col: "" for col in df.columns}

    # Fill in values from the extraction using the column map
    for key, value in extraction.items():
        mapped_col = column_map.get(key)
        if mapped_col in new_row:
            new_row[mapped_col] = value

    # Append the new row
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # Save the updated CSV (overwrite or save as new)
    df.to_csv("test.csv", index=False)

    print("Append done!",df.tail(1))
    return df.tail(1)

def extract_name_date(data):
    result = {
        "Name": data["Name"],
        "Invoice Date": data["Invoice Date"],
        "Total Amount": data["Total Amount"]
    }
    return json.dumps(result, indent=2)

def extract_table(data):
    rows = []
    for i in range(len(data["Medicine Description"])):
        rows.append([
            data["Medicine Description"][i],
            data["Qty"][i],
            data["Unit Price"][i],
            data["Amount"][i]
        ])
    return tabulate(rows, headers=["Description", "Quantity", "Unit Price","Amount"], tablefmt="grid")

def get_medicine_function(medicine_name):
    
# Configure
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = f"Explain in a simple sentence the main medical use or function of the medicine '{medicine_name}'."
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return "Function info not available"
