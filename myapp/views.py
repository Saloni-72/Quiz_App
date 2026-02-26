from django.shortcuts import render, redirect
from .models import Player, Subject, Question, Score

#Create your views here.
def welcome(request):
    return render(request, "welcome.html")

def home(request):
    subjects = Subject.objects.all()
    return render(request, "home.html", {"subjects": subjects})


def start_quiz(request):

    if request.method == "POST":

        # Start Quiz
        if not request.POST.get("player_id"):

            name = request.POST.get("name")
            subject_id = request.POST.get("subject")

            if not name or not subject_id:
                return redirect("home")

            player, created = Player.objects.get_or_create(name=name)
            subject = Subject.objects.get(id=subject_id)

            questions = Question.objects.filter(subject=subject).order_by('?')

            return render(request, "quiz.html", {
                "player": player,
                "subject": subject,
                "questions": questions
            })

        # Submit Quiz
        else:
            player_id = request.POST.get("player_id")
            subject_id = request.POST.get("subject_id")

            player = Player.objects.get(id=player_id)
            subject = Subject.objects.get(id=subject_id)

            score_count = 0
            total = 0
            user_answers = []

            for key in request.POST:
                if key not in ["csrfmiddlewaretoken", "player_id", "subject_id"]:
                    question = Question.objects.get(id=key)
                    selected = request.POST.get(key)

                    is_correct = selected == question.answer

                    if is_correct:
                        score_count += 1
                    total += 1

                    user_answers.append({
                        "question": question.question,
                        "selected": selected,
                        "correct_answer": question.answer,
                        "is_correct": is_correct
                    })

            percentage = (score_count / total) * 100 if total > 0 else 0

            # Save Score + Answers 
            saved_score, created = Score.objects.update_or_create(
                player=player,
                subject=subject,
                defaults={
                    "score": score_count,
                    "percentage": round(percentage, 2),
                    "answers": user_answers
                }
            )

            return redirect("result", score_id=saved_score.id)

    return redirect("home")


def result(request, score_id):
    score = Score.objects.select_related('player', 'subject').get(id=score_id)

    return render(request, "result.html", {
        "player": score.player,
        "subject": score.subject,
        "score": score.score,
        "total": len(score.answers) if score.answers else 0,
        "percentage": score.percentage,
        "answers": score.answers or []
    })


def leaderboard(request):
    scores = Score.objects.select_related('player', 'subject') \
        .order_by('-percentage')

    return render(request, "leaderboard.html", {"scores": scores})