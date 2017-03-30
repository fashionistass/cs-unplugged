from django.shortcuts import get_object_or_404
from django.views import generic

from topics.models import (
    Topic,
    CurriculumArea,
    CurriculumIntegration,
    UnitPlan,
    ProgrammingExercise,
    ProgrammingExerciseDifficulty,
    ProgrammingExerciseLanguage,
    ProgrammingExerciseLanguageImplementation,
    LearningOutcome,
)


class IndexView(generic.ListView):
    template_name = 'dev/index.html'
    context_object_name = 'all_topics'

    def get_queryset(self):
        """Return all topics"""
        return Topic.objects.order_by('name')

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)

        # Get topic, unit plan and lesson lists
        context['topics'] = Topic.objects.order_by('name')
        context['unit_plans'] = []

        # Build dictionaries for each unit plan and lesson
        for topic in context['topics']:
            topic.unit_plans = UnitPlan.objects.filter(topic=topic)
            for unit_plan in topic.unit_plans:
                unit_plan.lessons = unit_plan.lessons_by_age_group()
            topic.integrations = CurriculumIntegration.objects.filter(topic=topic)
            topic.programming_exercises = ProgrammingExercise.objects.filter(topic=topic)
            context['unit_plans'] += topic.unit_plans

        # Get curriculum area list
        context['curriculum_areas'] = {}
        for parent in CurriculumArea.objects.filter(parent=None):
            context['curriculum_areas'][parent] = [child for child in CurriculumArea.objects.filter(parent=parent)]

        # Get learning outcome list
        context['learning_outcomes'] = LearningOutcome.objects.all()

        # Get learning outcome list
        context['programming_exercise_languages'] = ProgrammingExerciseLanguage.objects.all()

        # Get learning outcome list
        context['programming_exercise_difficulties'] = ProgrammingExerciseDifficulty.objects.all()
        print(context['programming_exercise_difficulties'])

        return context


class ProgrammingExerciseView(generic.DetailView):
    model = ProgrammingExercise
    template_name = 'dev/programming_exercise.html'
    context_object_name = 'programming_exercise'

    def get_object(self, **kwargs):
        return get_object_or_404(
            self.model.objects.select_related(),
            slug=self.kwargs.get('programming_exercise_slug', None)
        )

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ProgrammingExerciseView, self).get_context_data(**kwargs)
        # Add all the connected learning outcomes
        context['programming_exercise_learning_outcomes'] = self.object.learning_outcomes.all()
        context['implementations'] = self.object.implementations.all().order_by('-language__name').select_related()
        return context


class ProgrammingExerciseLanguageSolutionView(generic.DetailView):
    model = ProgrammingExerciseLanguageImplementation
    template_name = 'dev/programming_exercise_language_solution.html'
    context_object_name = 'implementation'

    def get_object(self, **kwargs):
        return get_object_or_404(
            self.model.objects.select_related(),
            exercise__slug=self.kwargs.get('programming_exercise_slug', None),
            language__slug=self.kwargs.get('programming_language_slug', None)
        )

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ProgrammingExerciseLanguageSolutionView, self).get_context_data(**kwargs)
        context['programming_exercise'] = self.object.exercise
        return context


class CurriculumIntegrationView(generic.DetailView):
    model = CurriculumIntegration
    queryset = CurriculumIntegration.objects.all()
    template_name = 'dev/curriculum_integration.html'
    context_object_name = 'integration'

    def get_object(self, **kwargs):
        return get_object_or_404(
            self.model.objects.select_related(),
            slug=self.kwargs.get('integration_slug', None)
        )

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(CurriculumIntegrationView, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the connected curriculum areas
        context['integration_curriculum_areas'] = self.object.curriculum_areas.all()
        # Add in a QuerySet of all the prerequisite lessons
        context['prerequisite_lessons'] = self.object.prerequisite_lessons.select_related().order_by(
            'unit_plan__name', 'number'
        )
        return context
