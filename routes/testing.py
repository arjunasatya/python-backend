import pdfkit

# Ganti path jika perlu, atau pastikan wkhtmltopdf ada di PATH
config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')  # untuk Windows
# config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')  # untuk Linux
# config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')  # untuk macOS

html_content = '<html><body><h1>Hello, PDF!</h1><p>This is a test.</p></body></html>'
pdfkit.from_string(html_content, 'output.pdf', configuration=config)
print("PDF berhasil dibuat sebagai output.pdf")
