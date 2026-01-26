---
source: https://docs.mistral.ai/capabilities/document_ai/basic_ocr
---

# Document AI - OCR 3 Processor

Mistral Document AI API comes with a Document OCR (Optical Character Recognition) processor, powered by our latest OCR model `mistral-ocr-latest`, which enables you to extract text and structured content from PDF documents.

<SectionTab as="h1" sectionId="before-you-start">Before You Start</SectionTab>

## Key Features

- **Extracts text** in content while maintaining document structure and hierarchy.
- Preserves formatting like headers, paragraphs, lists and tables.
  - **Table formatting** can be toggled between `null`, `markdown` and `html` via the `table_format` parameter.
    - `null`: Tables are returned inline as markdown within the extracted page.
    - `markdown`: Tables are returned as markdown tables separately.
    - `html`: Tables are returned as html tables separately.
- Option to **extract headers and footers** via the `extract_header` and the `extract_footer` parameter, when used, the headers and footers content will be provided in the `header` and `footer` fields. By default, headers and footers are considered as part of the main content output.
- Returns results in markdown format for easy parsing and rendering.
- Handles complex layouts including multi-column text and mixed content and returns hyperlinks when available.
- Processes documents at scale with high accuracy
- Supports multiple document formats including:
  - `image_url`: png, jpeg/jpg, avif and more...
  - `document_url`: pdf, pptx, docx and more...
  - For a comprehensive list, visit the [Mistral documentation](https://docs.mistral.ai).

Learn more in the [OCR API documentation](https://docs.mistral.ai/api/endpoint/ocr).

:::info
Table formatting as well as header and footer extraction is only available for OCR 2512 or newer.
:::

The OCR processor returns the extracted **text content**, **images bboxes** and metadata about the document structure, making it easy to work with the recognized content programmatically.

<SectionTab as="h1" sectionId="ocr-images-and-pdfs">OCR with Images and PDFs</SectionTab>

## OCR your Documents

We provide different methods to OCR your documents. You can either OCR a **PDF** or an **Image**.

<SectionTab as="h2" variant="secondary" sectionId="ocr-pdfs">PDFs</SectionTab>

Among the PDF methods, you can use a **public available URL**, a **base64 encoded PDF** or by **uploading a PDF in our Cloud**.

<ExplorerTabs id="pdfs">
    <ExplorerTab value="pdf-url" label="OCR with a PDF Url">
        Be sure the URL is **public** and accessible by our API.

<Tabs groupId="code">
    <TabItem value="python" label="python">

```python
import os
from mistralai import Mistral

api_key = os.environ["MISTRAL_API_KEY"]

client = Mistral(api_key=api_key)

ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "document_url",
        "document_url": "https://arxiv.org/pdf/2201.04234"
    },
    table_format="html", # default is None
    # extract_header=True, # default is False
    # extract_footer=True, # default is False
    include_image_base64=True
)
```

  </TabItem>
  <TabItem value="typescript" label="typescript">

```typescript

const apiKey = process.env.MISTRAL_API_KEY;

const client = new Mistral({apiKey: apiKey});

const ocrResponse = await client.ocr.process({
    model: "mistral-ocr-latest",
    document: {
        type: "document_url",
        documentUrl: "https://arxiv.org/pdf/2201.04234"
    },
    tableFormat: "html", // default is null
    // extractHeader: False, // default is False
    // extractFooter: False, // default is False
    includeImageBase64: true
});
```

  </TabItem>
  <TabItem value="curl" label="curl">

```bash
curl https://api.mistral.ai/v1/ocr \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${MISTRAL_API_KEY}" \
  -d '{
    "model": "mistral-ocr-latest",
    "document": {
        "type": "document_url",
        "document_url": "https://arxiv.org/pdf/2201.04234"
    },
    "table_format": "html",
    "include_image_base64": true
  }' -o ocr_output.json
```

  </TabItem>
  <TabItem value="output" label="output">

```json
{
  "pages": [
    {
      "index": 0,
      "markdown": "# Document Title\n\nFirst paragraph of extracted text from the PDF...\n\n## Section Heading\n\nMore content follows here...",
      "images": [],
      "tables": [],
      "hyperlinks": ["https://example.com"],
      "header": null,
      "footer": null,
      "dimensions": {"dpi": 200, "height": 2200, "width": 1700}
    },
    {
      "index": 1,
      "markdown": "## Page 2 Content\n\n![img-0.jpeg](img-0.jpeg)\n\nText with embedded image reference...\n\n[tbl-0.html](tbl-0.html)\n\nTable caption text...",
      "images": [
        {
          "id": "img-0.jpeg",
          "top_left_x": 100,
          "top_left_y": 200,
          "bottom_right_x": 500,
          "bottom_right_y": 400,
          "image_base64": "data:image/jpeg;base64,...",
          "image_annotation": null
        }
      ],
      "tables": [
        {
          "id": "tbl-0.html",
          "content": "<table><tr><th>Header 1</th><th>Header 2</th></tr><tr><td>Cell 1</td><td>Cell 2</td></tr></table>",
          "format": "html"
        }
      ],
      "hyperlinks": [],
      "header": null,
      "footer": null,
      "dimensions": {"dpi": 200, "height": 2200, "width": 1700}
    }
  ],
  "model": "mistral-ocr-2512",
  "document_annotation": null,
  "usage_info": {"pages_processed": 2, "doc_size_bytes": 150000}
}
```

</TabItem>
</Tabs>
</ExplorerTab>
<ExplorerTab value="base64-encoded-pdf" label="OCR with a Base64 Encoded PDF">
        A method to upload local pdf files, is by **encoding them in base64 and passing them as a data url**.
<Tabs groupId="code">
    <TabItem value="python" label="python">

```python
import base64
import os
from mistralai import Mistral

api_key = os.environ["MISTRAL_API_KEY"]

client = Mistral(api_key=api_key)

def encode_pdf(pdf_path):
    with open(pdf_path, "rb") as pdf_file:
        return base64.b64encode(pdf_file.read()).decode('utf-8')

pdf_path = "path_to_your_pdf.pdf"
base64_pdf = encode_pdf(pdf_path)

ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "document_url",
        "document_url": f"data:application/pdf;base64,{base64_pdf}"
    },
    table_format="html", # default is None
    # extract_header=True, # default is False
    # extract_footer=True, # default is False
    include_image_base64=True
)
```

  </TabItem>
  <TabItem value="typescript" label="typescript">

```ts

const apiKey = process.env.MISTRAL_API_KEY;

const client = new Mistral({ apiKey: apiKey });

async function encodePdf(pdfPath) {
    const pdfBuffer = fs.readFileSync(pdfPath);
    const base64Pdf = pdfBuffer.toString('base64');
    return base64Pdf;
}

const pdfPath = "path_to_your_pdf.pdf";
const base64Pdf = await encodePdf(pdfPath);

const ocrResponse = await client.ocr.process({
    model: "mistral-ocr-latest",
    document: {
        type: "document_url",
        documentUrl: "data:application/pdf;base64," + base64Pdf
    },
    tableFormat: "html", // default is null
    // extractHeader: False, // default is False
    // extractFooter: False, // default is False
    includeImageBase64: true
});
```

  </TabItem>
  <TabItem value="curl" label="curl">

```bash
curl https://api.mistral.ai/v1/ocr \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${MISTRAL_API_KEY}" \
  -d '{
    "model": "mistral-ocr-latest",
    "document": {
        "type": "document_url",
        "document_url": "data:application/pdf;base64,<base64_pdf>"
    },
    "table_format": "html",
    "include_image_base64": true
  }' -o ocr_output.json
```

  </TabItem>
  <TabItem value="output" label="output">

See output structure above (same format as PDF URL method).

</TabItem>
</Tabs>
</ExplorerTab>
    <ExplorerTab value="with-uploaded-pdf" label="OCR with an Uploaded PDF">
        You can also upload a PDF file in our Cloud and get the OCR results from the uploaded PDF by retrieving a signed url.

<SectionTab as="h3" variant="secondary" sectionId="upload-a-file">Upload a File</SectionTab>

First, you will have to upload your PDF file to our cloud, this file will be stored and only accessible via an API key.

<Tabs groupId="code">
  <TabItem value="python" label="python" default>

```python
from mistralai import Mistral
import os

api_key = os.environ["MISTRAL_API_KEY"]

client = Mistral(api_key=api_key)

uploaded_pdf = client.files.upload(
    file={
        "file_name": "document.pdf",
        "content": open("document.pdf", "rb"),
    },
    purpose="ocr"
)
```

  </TabItem>
  <TabItem value="typescript" label="typescript">

```typescript

const apiKey = process.env.MISTRAL_API_KEY;

const client = new Mistral({apiKey: apiKey});

const uploadedFile = fs.readFileSync('document.pdf');
const uploadedPdf = await client.files.upload({
    file: {
        fileName: "document.pdf",
        content: uploadedFile,
    },
    purpose: "ocr"
});
```

  </TabItem>
  <TabItem value="curl" label="curl">

```bash
curl https://api.mistral.ai/v1/files \
  -H "Authorization: Bearer $MISTRAL_API_KEY" \
  -F purpose="ocr" \
  -F file="@document.pdf"
```

  </TabItem>
  <TabItem value="output" label="output">

```json
{
  "id": "22e2e88f-167d-4f3d-982a-add977a54ec3",
  "object": "file",
  "bytes": 3002783,
  "created_at": 1756464781,
  "filename": "document.pdf",
  "purpose": "ocr",
  "sample_type": "ocr_input",
  "num_lines": 0,
  "mimetype": "application/pdf",
  "source": "upload"
}
```

</TabItem>
</Tabs>

<SectionTab as="h3" variant="secondary" sectionId="retrieve-file">Retrieve File</SectionTab>

Once the file uploaded, you can retrieve it at any point.

<Tabs groupId="code">
  <TabItem value="python" label="python">

```python
retrieved_file = client.files.retrieve(file_id=uploaded_pdf.id)
```

  </TabItem>
  <TabItem value="typescript" label="typescript">

```typescript
const retrievedFile = await client.files.retrieve({
    fileId: uploadedPdf.id
});
```

  </TabItem>
  <TabItem value="curl" label="curl">

```bash
curl -X GET "https://api.mistral.ai/v1/files/$id" \
     -H "Accept: application/json" \
     -H "Authorization: Bearer $MISTRAL_API_KEY"
```

  </TabItem>

  <TabItem value="output" label="output">

```json
{
  "id": "22e2e88f-167d-4f3d-982a-add977a54ec3",
  "object": "file",
  "bytes": 3002783,
  "created_at": 1756464781,
  "filename": "document.pdf",
  "purpose": "ocr",
  "deleted": false
}
```

</TabItem>
</Tabs>

<SectionTab as="h3" variant="secondary" sectionId="get-signed-url">Get Signed Url</SectionTab>

For OCR tasks, you can get a signed url to access the file. An optional `expiry` parameter allow you to automatically expire the signed url after n hours.

<Tabs groupId="code">
  <TabItem value="python" label="python">

```python
signed_url = client.files.get_signed_url(file_id=uploaded_pdf.id)
```

  </TabItem>
  <TabItem value="typescript" label="typescript">

```typescript
const signedUrl = await client.files.getSignedUrl({
    fileId: uploadedPdf.id,
});
```

  </TabItem>
  <TabItem value="curl" label="curl">

```bash
curl -X GET "https://api.mistral.ai/v1/files/$id/url?expiry=24" \
     -H "Accept: application/json" \
     -H "Authorization: Bearer $MISTRAL_API_KEY"
```

  </TabItem>

  <TabItem value="output" label="output">

```json
{
  "url": "https://mistralaifilesapiprodswe.blob.core.windows.net/fine-tune/.../file.pdf?se=...&sp=r&sv=...&sr=b&sig=..."
}
```

</TabItem>
</Tabs>

<SectionTab as="h3" variant="secondary" sectionId="get-ocr-results">Get OCR Results</SectionTab>

You can now query the OCR endpoint with the signed url.

<Tabs groupId="code">
  <TabItem value="python" label="python">

```python
ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "document_url",
        "document_url": signed_url.url,
    },
    table_format="html", # default is None
    # extract_header=True, # default is False
    # extract_footer=True, # default is False
    include_image_base64=True
)
```

  </TabItem>
  <TabItem value="typescript" label="typescript">

```typescript
const ocrResponse = await client.ocr.process({
    model: "mistral-ocr-latest",
    document: {
        type: "document_url",
        documentUrl: signedUrl.url,
    },
    tableFormat: "html", // default is null
    // extractHeader: False, // default is False
    // extractFooter: False, // default is False
    includeImageBase64: true
});
```

  </TabItem>
  <TabItem value="curl" label="curl">

```bash
curl https://api.mistral.ai/v1/ocr \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${MISTRAL_API_KEY}" \
  -d '{
    "model": "mistral-ocr-latest",
    "document": {
        "type": "document_url",
        "document_url": "<signed_url>"
    },
    "table_format": "html",
    "include_image_base64": true
  }' -o ocr_output.json
```

</TabItem>

<TabItem value="output" label="output">

See output structure above (same format as PDF URL method).

</TabItem>
</Tabs>

<SectionTab as="h3" variant="secondary" sectionId="delete-file">Delete File</SectionTab>

Once all OCR done, you can optionally delete the pdf file from our cloud unless you wish to reuse it later.

<Tabs groupId="code">
  <TabItem value="python" label="python">

```python
client.files.delete(file_id=file.id)
```

  </TabItem>
  <TabItem value="typescript" label="typescript">

```typescript
await client.files.delete(fileId=file.id);
```

  </TabItem>
  <TabItem value="curl" label="curl">

```bash
curl -X DELETE https://api.mistral.ai/v1/files/${file_id} \
-H "Authorization: Bearer ${MISTRAL_API_KEY}"
```

  </TabItem>
  <TabItem value="output" label="output">

```json
{
"id": "22e2e88f-167d-4f3d-982a-add977a54ec3",
"object": "file",
"deleted": true
}
```

  </TabItem>
</Tabs>
    </ExplorerTab>
</ExplorerTabs>

The output will be a JSON object containing the extracted text content, images bboxes, metadata and other information about the document structure.

```py
{
  "pages": [ # The content of each page
    {
      "index": int, # The index of the corresponding page
      "markdown": str, # The main output and raw markdown content
      "images": list, # Image information when images are extracted
      "tables": list, # Table information when using `table_format=html` or `table_format=markdown`
      "hyperlinks": list, # Hyperlinks detected
      "header": str|null, # Header content when using `extract_header=True`
      "footer": str|null, # Footer content when using `extract_footer=True`
      "dimensions": dict # The dimensions of the page
    }
  ],
  "model": str, # The model used for the OCR
  "document_annotation": dict|null, # Document annotation information when used, visit the Annotations documentation for more information
  "usage_info": dict # Usage information
}
```

:::note
When extracting images and tables they will be replaced with placeholders, such as:

- `![img-0.jpeg](img-0.jpeg)`
- `[tbl-3.html](tbl-3.html)`

You can map them to the actual images and tables by using the `images` and `tables` fields.
:::

<SectionTab as="h2" variant="secondary" sectionId="ocr-images">Images</SectionTab>

To perform OCR on an image, you can either pass a URL to the image or directly use a Base64 encoded image.

<ExplorerTabs id="images">
    <ExplorerTab value="with-image-url" label="OCR with an Image URL">
        You can perform OCR with any public available image as long as a direct url is available.

<Tabs groupId="code">
  <TabItem value="python" label="python">

```python
import os
from mistralai import Mistral

api_key = os.environ["MISTRAL_API_KEY"]

client = Mistral(api_key=api_key)

ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "image_url",
        "image_url": "https://raw.githubusercontent.com/mistralai/cookbook/refs/heads/main/mistral/ocr/receipt.png"
    },
    # table_format=None,
    include_image_base64=True
)
```

  </TabItem>
  <TabItem value="typescript" label="typescript">

```typescript

const apiKey = process.env.MISTRAL_API_KEY;

const client = new Mistral({apiKey: apiKey});

const ocrResponse = await client.ocr.process({
    model: "mistral-ocr-latest",
    document: {
        type: "image_url",
        imageUrl: "https://raw.githubusercontent.com/mistralai/cookbook/refs/heads/main/mistral/ocr/receipt.png",
    },
    // tableFormat: null,
    includeImageBase64: true
});
```

  </TabItem>
  <TabItem value="curl" label="curl">

```bash
curl https://api.mistral.ai/v1/ocr \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${MISTRAL_API_KEY}" \
  -d '{
    "model": "mistral-ocr-latest",
    "document": {
        "type": "image_url",
        "image_url": "https://raw.githubusercontent.com/mistralai/cookbook/refs/heads/main/mistral/ocr/receipt.png"
    },
    "include_image_base64": true
  }' -o ocr_output.json
```

  </TabItem>
  <TabItem value="output" label="output">
```json
{
  "pages": [
    {
      "index": 0,
      "markdown": "PLACE FACE UP ON DASH\nCITY OF PALO ALTO\nNOT VALID FOR\nONSTREET PARKING\n\nExpiration Date/Time\n11:59 PM\nAUG 19, 2024\n\nPurchase Date/Time: 01:34pm Aug 19, 2024\nTotal Due: $15.00\nTotal Paid: $15.00\nTicket #: 00005883",
      "images": [],
      "dimensions": {"dpi": 200, "height": 3210, "width": 1806}
    }
  ],
  "model": "mistral-ocr-2505-completion",
  "document_annotation": null,
  "usage_info": {"pages_processed": 1, "doc_size_bytes": 3110191}
}
```
    </TabItem>
</Tabs>
    </ExplorerTab>
    <ExplorerTab value="with-image-base64" label="OCR with a Base64 encoded Image">
        You can perform OCR with any public available image as long as a direct url is available.

<Tabs groupId="code">
  <TabItem value="python" label="python">

```python
import base64
import os
from mistralai import Mistral

api_key = os.environ["MISTRAL_API_KEY"]

client = Mistral(api_key=api_key)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

image_path = "path_to_your_image.jpg"
base64_image = encode_image(image_path)

ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "image_url",
        "image_url": f"data:image/jpeg;base64,{base64_image}"
    },
    # table_format=None,
    include_image_base64=True
)
```

  </TabItem>
  <TabItem value="typescript" label="typescript">

```ts

const apiKey = process.env.MISTRAL_API_KEY;

const client = new Mistral({ apiKey: apiKey });

async function encodeImage(imagePath) {
    const imageBuffer = fs.readFileSync(imagePath);
    const base64Image = imageBuffer.toString('base64');
    return base64Image;
}

const imagePath = "path_to_your_image.jpg";
const base64Image = await encodeImage(imagePath);

const ocrResponse = await client.ocr.process({
    model: "mistral-ocr-latest",
    document: {
        type: "image_url",
        imageUrl: "data:image/jpeg;base64," + base64Image
    },
    // tableFormat: null,
    includeImageBase64: true
});
```

  </TabItem>
  <TabItem value="curl" label="curl">

```bash
curl https://api.mistral.ai/v1/ocr \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${MISTRAL_API_KEY}" \
  -d '{
    "model": "mistral-ocr-latest",
    "document": {
        "type": "image_url",
        "image_url": "data:image/jpeg;base64,<base64_image>"
    },
    "include_image_base64": true
  }' -o ocr_output.json
```

</TabItem>
<TabItem value="output" label="output">

See output structure above (same format as Image URL method).

</TabItem>
</Tabs>
</ExplorerTab>
</ExplorerTabs>

The output will be a JSON object containing the extracted text content, images bboxes, metadata and other information about the document structure.

```py
{
  "pages": [ # The content of each page
    {
      "index": int, # The index of the corresponding page
      "markdown": str, # The main output and raw markdown content
      "images": list, # Image information when images are extracted
      "tables": list, # Table information when using `table_format=html` or `table_format=markdown`
      "hyperlinks": list, # Hyperlinks detected
      "header": str|null, # Header content when using `extract_header=True`
      "footer": str|null, # Footer content when using `extract_footer=True`
      "dimensions": dict # The dimensions of the page
    }
  ],
  "model": str, # The model used for the OCR
  "document_annotation": dict|null, # Document annotation information when used, visit the Annotations documentation for more information
  "usage_info": dict # Usage information
}
```

:::note
When extracting images and tables they will be replaced with placeholders, such as:

- `![img-0.jpeg](img-0.jpeg)`
- `[tbl-3.html](tbl-3.html)`

You can map them to the actual images and tables by using the `images` and `tables` fields.
:::

<SectionTab as="h1" sectionId="ocr-at-scale">OCR at Scale</SectionTab>

When performing OCR at scale, we recommend using our [Batch Inference service](../batch), this allows you to process large amounts of documents in parallel while being more cost-effective than using the OCR API directly. We also support [Annotations](annotations) for structured outputs and other features.

<SectionTab as="h1" sectionId="cookbooks">Cookbooks</SectionTab>

For more information and guides on how to make use of OCR, we have the following cookbooks:

- [Tool Use](https://colab.research.google.com/github/mistralai/cookbook/blob/main/mistral/ocr/tool_usage.ipynb)
- [Batch OCR](https://colab.research.google.com/github/mistralai/cookbook/blob/main/mistral/ocr/batch_ocr.ipynb)

<SectionTab as="h1" sectionId="faq">FAQ</SectionTab>

<Faq>
  <FaqItem question="Are there any limits regarding the OCR API?">
    Yes, there are certain limitations for the OCR API. Uploaded document files must not exceed 50 MB in size and should be no longer than 1,000 pages.
  </FaqItem>
  <FaqItem question="What document types are supported?">
Our Document AI OCR Processor supports a vast range of document and image types.

Below you can find a non-exhaustive list of the supported formats:

| Documents                          | Images               |
|------------------------------------|----------------------|
| **PDF** (.pdf)                     | **JPEG** (.jpg, .jpeg) |
| **Word Documents** (.docx)         | **PNG** (.png)       |
| **PowerPoint** (.pptx)             | **AVIF** (.avif)     |
| **Text Files** (.txt)              | **TIFF** (.tiff)     |
| **EPUB** (.epub)                   | **GIF** (.gif)       |
| **XML/DocBook** (.xml)             | **HEIC/HEIF** (.heic, .heif) |
| **RTF** (.rtf)                     | **BMP** (.bmp)       |
| **OpenDocument Text** (.odt)       | **WebP** (.webp)     |
| **BibTeX/BibLaTeX** (.bib)         |                      |
| **FictionBook** (.fb2)             |                      |
| **Jupyter Notebooks** (.ipynb)     |                      |
| **JATS XML** (.xml)                |                      |
| **LaTeX** (.tex)                   |                      |
| **OPML** (.opml)                   |                      |
| **Troff** (.1, .man)               |                      |

  </FaqItem>
</Faq>
