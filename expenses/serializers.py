from rest_framework import serializers
from .models import User, Expense, ExpenseSplit

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'mobile_number']

class ExpenseSplitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseSplit
        fields = ['user', 'amount', 'percentage']

class ExpenseSerializer(serializers.ModelSerializer):
    splits = ExpenseSplitSerializer(many=True)

    class Meta:
        model = Expense
        fields = ['id', 'description', 'amount', 'created_by', 'split_method', 'splits', 'created_at']

    def validate_splits(self, splits):
        split_method = self.initial_data.get('split_method')
        total_amount = float(self.initial_data.get('amount', 0))

        if split_method == 'EQUAL':
            return splits

        if split_method == 'EXACT':
            total_split = sum(float(split['amount']) for split in splits)
            if abs(total_split - total_amount) > 0.01:
                raise serializers.ValidationError("The sum of split amounts must equal the total expense amount.")

        if split_method == 'PERCENTAGE':
            total_percentage = sum(float(split['percentage']) for split in splits)
            if abs(total_percentage - 100) > 0.01:
                raise serializers.ValidationError("The sum of percentages must equal 100%.")

        return splits

    def create(self, validated_data):
        splits_data = validated_data.pop('splits')
        expense = Expense.objects.create(**validated_data)

        for split_data in splits_data:
            ExpenseSplit.objects.create(expense=expense, **split_data)

        return expense

class BalanceSheetSerializer(serializers.Serializer):
    user = UserSerializer()
    balance = serializers.DecimalField(max_digits=10, decimal_places=2)
