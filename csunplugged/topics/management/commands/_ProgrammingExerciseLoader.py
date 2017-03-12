from utils.BaseLoader import BaseLoader
from topics.models import (
    LearningOutcome,
    ProgrammingExerciseDifficulty,
    ProgrammingExerciseLanguage,
    ProgrammingExerciseLanguageImplementation,
)


class ProgrammingExerciseLoader(BaseLoader):
    """Loader for a programming exercise"""

    def __init__(self, load_log, exercise_slug, exercise_structure, topic, BASE_PATH):
        """Initiates the loader for a programming exercise

        Args:
            exercise_slug (string): slug for exercise
            exercise_structure (dict): attributes for exercise
            topic: Topic model object
        """
        super().__init__(BASE_PATH, load_log)
        self.exercise_slug = exercise_slug
        self.exercise_structure = exercise_structure
        self.topic = topic

    def load(self):
        """load the content for a programming exercise"""
        content = self.convert_md_file(self.BASE_PATH.format(self.exercise_structure['md-file']))

        programming_exercise = self.topic.topic_programming_exercises.create(
            slug=self.exercise_slug,
            name=content.title,
            exercise_number=self.exercise_structure['number'],
            content=content.html_string,
            difficulty=ProgrammingExerciseDifficulty.objects.get(
                level=self.exercise_structure['difficulty-level']
            )
        )
        programming_exercise.save()

        language_solutions = self.exercise_structure['programming-languages']
        for language in language_solutions:
            # This gets the language for the solution, if not found it should throw an error!
            language_object = ProgrammingExerciseLanguage.objects.get(
                slug=language
            )
            hint_path = self.BASE_PATH.format(language_solutions[language]['hints'])
            hint_content = self.convert_md_file(hint_path).html_string

            solution_path = self.BASE_PATH.format(language_solutions[language]['solution'])
            solution_content = self.convert_md_file(solution_path).html_string

            implementation = ProgrammingExerciseLanguageImplementation.objects.create(
                hints=hint_content,
                solution=solution_content,
                language=language_object,
                exercise=programming_exercise,
                topic=self.topic
            )
            implementation.save()

        for learning_outcome_slug in self.exercise_structure['learning-outcomes']:
            learning_outcome = LearningOutcome.objects.get(
                slug=learning_outcome_slug
            )
            programming_exercise.learning_outcomes.add(learning_outcome)

        LOG_TEMPLATE = 'Added Programming Exercise: {}'
        self.log(LOG_TEMPLATE.format(programming_exercise.name), 1)
