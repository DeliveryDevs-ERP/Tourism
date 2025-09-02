import subprocess
import tempfile
import frappe
from frappe.utils.jinja import get_jenv

def get_pdf_puppeteer(html_content):
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as html_file:
        html_file.write(html_content.encode("utf-8"))
        html_file.flush()
        output_pdf = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False).name

        subprocess.run([
            "node", "/path/to/puppeteer_pdf.js", html_file.name, output_pdf
        ], check=True)

        with open(output_pdf, "rb") as f:
            pdf_data = f.read()

    return pdf_data

# Override frappe’s default get_pdf
import frappe.utils.pdf
frappe.utils.pdf.get_pdf = get_pdf_puppeteer