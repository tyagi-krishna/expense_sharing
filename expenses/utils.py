from django.db.models import Sum
from .models import User, Expense, ExpenseSplit
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO

def calculate_balances():
    users = User.objects.all()
    balances = []

    for user in users:
        paid = Expense.objects.filter(created_by=user).aggregate(total=Sum('amount'))['total'] or 0
        owed = ExpenseSplit.objects.filter(user=user).aggregate(total=Sum('amount'))['total'] or 0
        balance = paid - owed
        balances.append({"user": user, "balance": balance})

    return balances

def generate_balance_sheet_pdf(balances):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setFont("Helvetica", 12)

    p.drawString(100, 750, "Balance Sheet")
    y = 700

    for balance in balances:
        user = balance['user']
        amount = balance['balance']
        p.drawString(100, y, f"{user.name}: ${amount:.2f}")
        y -= 20

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    return pdf
