# Smart Task Analyzer

## Setup Instructions
 1. Clone repository
git clone <your repo url>
cd project-folder

 2. Create virtual environment
python -m venv venv
.\venv\Scripts\activate

 3. Install dependencies
pip install -r requirements.txt

 4. Run migrations
python manage.py migrate

 5. Start backend server
python manage.py runserver 127.0.0.1:8001


# Your backend API will be available at:

http://127.0.0.1:8001/api/tasks/analyze/



## Frontend 

cd frontend
npm install
npm run dev


## Algorithm Explanation


The system assigns every task a priority score from 0–100 using a multi-dimensional scoring algorithm that models real-world human decision-making. The aim is to balance urgency, importance, effort, and dependency impact into a single comparable value.

1. Urgency Score

Urgency reflects how soon a task is due.
We calculate urgency as:

Overdue tasks → urgency = 1.0

Tasks due within 24 hours → urgency ≈ 0.9–1.0

Within 3–5 days → moderate urgency

10 days → low urgency

This is implemented using an exponential decay curve (1 / days_left*k), producing a smooth gradient rather than a binary deadline check.

2. Importance Score

Importance (1–10) is normalized to a 0–1 scale.
Higher importance = stronger impact on final score.
This reflects management principles where essential tasks should not be overshadowed by near deadlines.

3. Effort Score (inverse)

Effort is computed as an inverse weight:

effort_score = 1 / (estimated_hours + 1)


This rewards small tasks (“quick wins”) because they unblock progress and maintain momentum with minimal cost.

4. Dependency Score

Tasks often unlock other tasks. A task with many dependents receives higher priority.
We count how many tasks depend on this task directly or indirectly.
More unblocked tasks = higher dependency value.

5. Circular Dependency Detection

The system uses DFS cycle detection to find loops such as:

A → B → C → A


When a cycle exists:

The cycle is returned in result.cycles

All tasks within the cycle receive score = null

Tasks remain visible but flagged as structurally invalid

6. Weighted Strategy

We support 4 scoring strategies:

Strategy	Behavior
smart_balance	Evenly weights urgency, importance, effort, dependencies
high_impact	Strongly favors importance
fastest_wins	Favors small tasks first
deadline_driven	Favors urgent items heavily

Each strategy uses different weights but the same underlying scoring components.

Final Score
score = (urgency*w1 + importance*w2 + effort*w3 + dependency*w4) * 100


This produces a human-interpretable priority ranking suitable for planning, scheduling, and performance optimization.


## Design Decisions

Django + DRF Backend

Chosen for:

Strong validation (serializers)

Stable routing & ORM

Ability to scale into a full backend system

React + Vite Frontend

Instant refresh, very fast build times

Clean component architecture

Modern dev environment

Vis-Network for Graph

Chosen because:

Smooth physics and auto-layout

Built-in arrows, smooth edges

Easy node highlighting

High configurability

JSON Input Design

Tasks are provided as JSON to make the system:

Simple for testing

Compatible with future AI-generated inputs

Easy to copy/paste between backend and UI

No database used

For this assignment, tasks are transient and processed in-memory.

Color-coded urgency

We map urgency to:

Red: overdue or extremely urgent

Orange: approaching soon

Green: comfortable schedule

This improves visual scanning.