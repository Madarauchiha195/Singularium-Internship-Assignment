# tasks/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TaskSerializer
from .scoring import compute_scores
from rest_framework.decorators import api_view

class AnalyzeView(APIView):
    def post(self, request, format=None):
        data = request.data
        if isinstance(data, dict) and 'tasks' in data:
            tasks_input = data['tasks']
            strategy = data.get('strategy', 'smart_balance')
        elif isinstance(data, list):
            tasks_input = data
            strategy = request.query_params.get('strategy', 'smart_balance')
        else:
            return Response({"detail": "Invalid payload. Send a JSON list of tasks or {\"tasks\": [...]}."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TaskSerializer(data=tasks_input, many=True)
        if not serializer.is_valid():
            return Response({"detail": "Invalid task data", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        tasks = serializer.validated_data
        result = compute_scores(tasks, strategy=strategy)
        return Response(result, status=status.HTTP_200_OK)

@api_view(['GET'])
def suggest_view(request):
    import json
    strategy = request.query_params.get('strategy', 'smart_balance')
    tasks_param = request.query_params.get('tasks')
    if not tasks_param:
        return Response({"detail": "Provide tasks via ?tasks=[JSON] or POST to /api/tasks/analyze/ and use that."}, status=400)
    try:
        tasks = json.loads(tasks_param)
    except Exception:
        return Response({"detail": "Invalid tasks parameter (expect JSON)."}, status=400)
    result = compute_scores(tasks, strategy=strategy)
    filtered = [t for t in result['tasks'] if t['score'] is not None]
    top3 = filtered[:3]
    return Response({"strategy": strategy, "suggestions": top3, "cycles": result['cycles'], "warnings": result['warnings']})
