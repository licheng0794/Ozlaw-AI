from django.shortcuts import render
from .rag_pipeline import answer_question

# OzLaw AI: Main view for legal Q&A

def home(request):
    answer = None
    question = None
    # Get conversation history from session or initialize
    history = request.session.get('history', [])

    if request.method == 'POST':
        question = request.POST.get('question')
        if question:
            # Pass history to answer_question for context
            answer = answer_question(question, history=history)
            # Add to history
            history.append({'question': question, 'answer': answer})
            # Save back to session
            request.session['history'] = history

    return render(request, 'legal_ai/index.html', {
        'answer': answer,
        'question': question,
        'history': history
    }) 