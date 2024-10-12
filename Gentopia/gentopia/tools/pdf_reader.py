from typing import AnyStr, Optional, Type
from gentopia.tools.basetool import *
from pydantic import BaseModel, Field
import PyPDF2
import requests
import os

class PDFReaderArgs(BaseModel):
    file_path_or_url: str = Field(..., description="The path or URL to the PDF file")

class PDFReaderTool(BaseTool):
    """Tool that reads and extracts text from PDF files or from URLs pointing to PDFs."""
    
    name = "pdf_reader"
    description = ("A tool that reads PDF files and extracts the text from them. "
                   "Input can be a local file path or a URL to a PDF.")

    args_schema: Optional[Type[BaseModel]] = PDFReaderArgs

    def _run(self, file_path_or_url: AnyStr) -> str:
        try:
            if file_path_or_url.startswith("http://") or file_path_or_url.startswith("https://"):
                # Extract the file name from the URL
                file_name = self.get_file_name_from_url(file_path_or_url)
                
                # Download the PDF from the URL and save it with the file name from the URL
                pdf_content = self.download_pdf(file_path_or_url)
                if not pdf_content:
                    return f"Unable to access the PDF at {file_path_or_url}. Please check the URL."
                
                with open(file_name, "wb") as pdf_file:
                    pdf_file.write(pdf_content)
                
                file_path = file_name
            else:
                # Input is a local file path
                file_path = file_path_or_url
            
            # Read and extract text from the PDF file
            return self.extract_text_from_pdf(file_path)
        
        except Exception as e:
            return f"Error processing PDF: {e}"
        
        finally:
            # Clean up the temporary file if it exists
            if file_path_or_url.startswith("http://") or file_path_or_url.startswith("https://"):
                if os.path.exists(file_name):
                    os.remove(file_name)

    def get_file_name_from_url(self, url: str) -> str:
        """Extract the file name from a URL."""
        return url.split("/")[-1]

    def download_pdf(self, url: str) -> Optional[bytes]:
        """Download a PDF from a URL, handling errors like 404."""
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.content
            else:
                return None
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error while downloading the PDF: {e}")

    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from a local PDF file."""
        try:
            with open(file_path, "rb") as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                text = ""
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
                    else:
                        print(f"Warning: No text found on one of the pages in {file_path}.")
                return text if text else "No text could be extracted from the PDF."
        except Exception as e:
            raise Exception(f"Error reading PDF file {file_path}: {e}")

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

if __name__ == "__main__":
    # Example usage with a local file path
    ans = PDFReaderTool()._run("sample.pdf")
    print(ans)

    # Example usage with URL
    ans = PDFReaderTool()._run("https://example.com/sample.pdf")
    print(ans)
