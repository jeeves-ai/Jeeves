import pandas as pd
import matplotlib.pyplot as plt
from models import FinancialRecord, Session


class PDFGenerator:
    @staticmethod
    def generate_pdf_report(user_id):
        session = Session()
        financial_records = session.query(FinancialRecord).filter_by(user_id=user_id).all()

        if not financial_records:
            session.close()
            return "No financial records found for the specified user."

        data = []
        for record in financial_records:
            data.append([record.username, record.user_message, record.product, record.price,
                         record.quantity, record.status, record.amount, record.timestamp])

        df = pd.DataFrame(data, columns=["Username", "User Message", "Product", "Price",
                                         "Quantity", "Status", "Amount", "Timestamp"])

        pdf_filename = f"financial_report_user_{user_id}.pdf"

        fig, ax = plt.subplots(figsize=(10, 6))

        ax.axis('off')

        header = ["Username", "User Message", "Product", "Price",
                  "Quantity", "Status", "Amount", "Timestamp"]

        table = ax.table(cellText=[header] + df.values.tolist(),
                         colLabels=None, cellLoc='center', loc='top', colColours=['#f2f2f2'] * len(header),
                         cellColours=[['#f2f2f2'] * len(header)] + [['#ffffff'] * len(header) for _ in range(len(df))])

        table.auto_set_font_size(False)
        table.set_fontsize(5)
        table.scale(1, 1.5)

        plt.savefig(pdf_filename, format='pdf', bbox_inches='tight')

        plt.close()

        session.close()
        return pdf_filename
