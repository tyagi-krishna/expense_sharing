from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from .models import User, Expense
from .serializers import UserSerializer, ExpenseSerializer, BalanceSheetSerializer
from .utils import calculate_balances, generate_balance_sheet_pdf

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

    @action(detail=False, methods=['GET'])
    def user_expenses(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        expenses = Expense.objects.filter(splits__user_id=user_id)
        serializer = self.get_serializer(expenses, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def overall_expenses(self, request):
        expenses = Expense.objects.all()
        total = expenses.aggregate(total=Sum('amount'))['total']
        return Response({"total_expenses": total})

    @action(detail=False, methods=['GET'])
    def balance_sheet(self, request):
        balances = calculate_balances()
        serializer = BalanceSheetSerializer(balances, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def download_balance_sheet(self, request):
        balances = calculate_balances()
        pdf = generate_balance_sheet_pdf(balances)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="balance_sheet.pdf"'
        return response
