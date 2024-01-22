from jinja2 import Template


def generate_html_report(financial_records):
    with open("templates/report.html", "r") as template_file:
        template_content = template_file.read()

    template = Template(template_content)

    html_content = template.render(financial_records=financial_records)

    return html_content
