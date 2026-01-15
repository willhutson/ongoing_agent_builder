"""
Training Progress Tracking

Tracks user progress through training courses, supporting multi-tenant isolation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class LessonStatus(Enum):
    """Status of a lesson for a user."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"  # For quizzes that weren't passed


@dataclass
class LessonProgress:
    """Tracks progress on a single lesson."""
    lesson_id: str
    status: LessonStatus = LessonStatus.NOT_STARTED
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    time_spent_seconds: int = 0
    quiz_score: Optional[int] = None
    attempts: int = 0


@dataclass
class ModuleProgress:
    """Tracks progress on a module."""
    module_id: str
    lesson_progress: dict[str, LessonProgress] = field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    @property
    def completion_percentage(self) -> float:
        if not self.lesson_progress:
            return 0.0
        completed = sum(1 for lp in self.lesson_progress.values() if lp.status == LessonStatus.COMPLETED)
        return (completed / len(self.lesson_progress)) * 100

    @property
    def is_complete(self) -> bool:
        return self.completion_percentage == 100


@dataclass
class CourseProgress:
    """Tracks user progress on a course."""
    course_id: str
    user_id: str
    organization_id: str  # Multi-tenant isolation
    module_progress: dict[str, ModuleProgress] = field(default_factory=dict)
    enrolled_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    certificate_issued: bool = False
    certificate_issued_at: Optional[datetime] = None

    @property
    def completion_percentage(self) -> float:
        if not self.module_progress:
            return 0.0
        total = sum(mp.completion_percentage for mp in self.module_progress.values())
        return total / len(self.module_progress)

    @property
    def is_complete(self) -> bool:
        return all(mp.is_complete for mp in self.module_progress.values())


@dataclass
class UserTrainingProfile:
    """Complete training profile for a user."""
    user_id: str
    organization_id: str
    course_progress: dict[str, CourseProgress] = field(default_factory=dict)
    total_time_spent_seconds: int = 0
    certificates_earned: list[str] = field(default_factory=list)
    agent_access_unlocked: list[str] = field(default_factory=list)

    def get_recommended_courses(self, all_courses: list) -> list:
        """Get courses recommended for this user based on progress."""
        recommendations = []
        for course in all_courses:
            # Skip completed courses
            if course.id in self.course_progress:
                progress = self.course_progress[course.id]
                if progress.is_complete:
                    continue
                # Recommend in-progress courses
                if progress.started_at and not progress.completed_at:
                    recommendations.insert(0, course)  # Prioritize in-progress
                    continue

            # Check prerequisites
            prerequisites_met = True
            for module in course.modules:
                for prereq in module.prerequisites:
                    # Find if prereq module is completed in any course
                    prereq_completed = any(
                        prereq in cp.module_progress and cp.module_progress[prereq].is_complete
                        for cp in self.course_progress.values()
                    )
                    if not prereq_completed:
                        prerequisites_met = False
                        break
                if not prerequisites_met:
                    break

            if prerequisites_met:
                recommendations.append(course)

        return recommendations


class ProgressTracker:
    """
    Service for tracking training progress.

    In production, this would persist to database.
    Here we provide the interface for the ERP to implement.
    """

    def __init__(self, storage_callback=None):
        """
        Initialize progress tracker.

        Args:
            storage_callback: Async function to persist progress to database
        """
        self.storage_callback = storage_callback
        self._profiles: dict[str, UserTrainingProfile] = {}  # In-memory for demo

    def get_user_profile(self, user_id: str, organization_id: str) -> UserTrainingProfile:
        """Get or create a user's training profile."""
        key = f"{organization_id}:{user_id}"
        if key not in self._profiles:
            self._profiles[key] = UserTrainingProfile(
                user_id=user_id,
                organization_id=organization_id,
            )
        return self._profiles[key]

    async def enroll_user(
        self,
        user_id: str,
        organization_id: str,
        course_id: str,
    ) -> CourseProgress:
        """Enroll a user in a course."""
        profile = self.get_user_profile(user_id, organization_id)

        if course_id in profile.course_progress:
            return profile.course_progress[course_id]

        progress = CourseProgress(
            course_id=course_id,
            user_id=user_id,
            organization_id=organization_id,
        )
        profile.course_progress[course_id] = progress

        if self.storage_callback:
            await self.storage_callback("enroll", progress)

        return progress

    async def start_lesson(
        self,
        user_id: str,
        organization_id: str,
        course_id: str,
        module_id: str,
        lesson_id: str,
    ) -> LessonProgress:
        """Mark a lesson as started."""
        profile = self.get_user_profile(user_id, organization_id)
        course_progress = profile.course_progress.get(course_id)

        if not course_progress:
            course_progress = await self.enroll_user(user_id, organization_id, course_id)

        # Initialize module progress if needed
        if module_id not in course_progress.module_progress:
            course_progress.module_progress[module_id] = ModuleProgress(
                module_id=module_id,
                started_at=datetime.now(),
            )

        module_progress = course_progress.module_progress[module_id]

        # Initialize or update lesson progress
        if lesson_id not in module_progress.lesson_progress:
            module_progress.lesson_progress[lesson_id] = LessonProgress(
                lesson_id=lesson_id,
            )

        lesson_progress = module_progress.lesson_progress[lesson_id]
        if lesson_progress.status == LessonStatus.NOT_STARTED:
            lesson_progress.status = LessonStatus.IN_PROGRESS
            lesson_progress.started_at = datetime.now()
            lesson_progress.attempts += 1

        # Update course started_at if first lesson
        if not course_progress.started_at:
            course_progress.started_at = datetime.now()

        if self.storage_callback:
            await self.storage_callback("start_lesson", lesson_progress)

        return lesson_progress

    async def complete_lesson(
        self,
        user_id: str,
        organization_id: str,
        course_id: str,
        module_id: str,
        lesson_id: str,
        quiz_score: Optional[int] = None,
        time_spent_seconds: int = 0,
    ) -> LessonProgress:
        """Mark a lesson as completed."""
        profile = self.get_user_profile(user_id, organization_id)
        course_progress = profile.course_progress.get(course_id)

        if not course_progress or module_id not in course_progress.module_progress:
            raise ValueError("Lesson not started")

        module_progress = course_progress.module_progress[module_id]
        lesson_progress = module_progress.lesson_progress.get(lesson_id)

        if not lesson_progress:
            raise ValueError("Lesson not started")

        lesson_progress.status = LessonStatus.COMPLETED
        lesson_progress.completed_at = datetime.now()
        lesson_progress.time_spent_seconds += time_spent_seconds
        if quiz_score is not None:
            lesson_progress.quiz_score = quiz_score

        # Update total time
        profile.total_time_spent_seconds += time_spent_seconds

        # Check if module is complete
        if module_progress.is_complete:
            module_progress.completed_at = datetime.now()

        # Check if course is complete
        if course_progress.is_complete:
            course_progress.completed_at = datetime.now()

        if self.storage_callback:
            await self.storage_callback("complete_lesson", lesson_progress)

        return lesson_progress

    async def issue_certificate(
        self,
        user_id: str,
        organization_id: str,
        course_id: str,
    ) -> bool:
        """Issue a certificate for course completion."""
        profile = self.get_user_profile(user_id, organization_id)
        course_progress = profile.course_progress.get(course_id)

        if not course_progress or not course_progress.is_complete:
            return False

        if course_progress.certificate_issued:
            return True

        course_progress.certificate_issued = True
        course_progress.certificate_issued_at = datetime.now()
        profile.certificates_earned.append(course_id)

        if self.storage_callback:
            await self.storage_callback("certificate", course_progress)

        return True

    def get_course_stats(self, course_id: str, organization_id: str) -> dict:
        """Get statistics for a course within an organization."""
        enrolled = 0
        completed = 0
        in_progress = 0
        avg_completion = 0.0
        completion_percentages = []

        for key, profile in self._profiles.items():
            if not key.startswith(f"{organization_id}:"):
                continue

            if course_id in profile.course_progress:
                enrolled += 1
                progress = profile.course_progress[course_id]
                completion_percentages.append(progress.completion_percentage)

                if progress.is_complete:
                    completed += 1
                elif progress.started_at:
                    in_progress += 1

        if completion_percentages:
            avg_completion = sum(completion_percentages) / len(completion_percentages)

        return {
            "course_id": course_id,
            "organization_id": organization_id,
            "enrolled": enrolled,
            "completed": completed,
            "in_progress": in_progress,
            "not_started": enrolled - completed - in_progress,
            "avg_completion_percentage": round(avg_completion, 1),
        }

    def get_organization_training_stats(self, organization_id: str) -> dict:
        """Get overall training stats for an organization."""
        total_users = 0
        total_enrollments = 0
        total_completions = 0
        total_time_spent = 0
        certificates_issued = 0

        for key, profile in self._profiles.items():
            if not key.startswith(f"{organization_id}:"):
                continue

            total_users += 1
            total_enrollments += len(profile.course_progress)
            total_completions += sum(
                1 for cp in profile.course_progress.values() if cp.is_complete
            )
            total_time_spent += profile.total_time_spent_seconds
            certificates_issued += len(profile.certificates_earned)

        return {
            "organization_id": organization_id,
            "total_users": total_users,
            "total_enrollments": total_enrollments,
            "total_completions": total_completions,
            "certificates_issued": certificates_issued,
            "total_training_hours": round(total_time_spent / 3600, 1),
            "avg_courses_per_user": round(total_enrollments / total_users, 1) if total_users else 0,
        }
