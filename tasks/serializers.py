from rest_framework import serializers

class TaskSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField(required=False, allow_blank=True)
    due_date = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    estimated_hours = serializers.FloatField(required=False, default=4.0)
    importance = serializers.IntegerField(required=False, default=5, min_value=1, max_value=10)
    dependencies = serializers.ListField(child=serializers.CharField(), required=False, default=list)
