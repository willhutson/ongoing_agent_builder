"""
SpokeStack Agent Training System

Provides structured LMS-compatible training content for agency teams
to learn and effectively use the agent capabilities within SpokeStack.

All training content is agent-specific (not industry-specific) to support
multi-tenant usage across different professional service verticals.
"""

from .courses import (
    TrainingCourse,
    TrainingModule,
    TrainingLesson,
    CourseLevel,
    LessonType,
    get_all_courses,
    get_course_by_id,
    get_courses_for_agent,
    get_courses_for_role,
    get_courses_by_level,
)
from .content import AgentTrainingContent, AgentGuide, ToolGuide
from .progress import (
    ProgressTracker,
    CourseProgress,
    ModuleProgress,
    LessonProgress,
    UserTrainingProfile,
    LessonStatus,
)

__all__ = [
    # Course definitions
    "TrainingCourse",
    "TrainingModule",
    "TrainingLesson",
    "CourseLevel",
    "LessonType",
    "get_all_courses",
    "get_course_by_id",
    "get_courses_for_agent",
    "get_courses_for_role",
    "get_courses_by_level",
    # Content
    "AgentTrainingContent",
    "AgentGuide",
    "ToolGuide",
    # Progress tracking
    "ProgressTracker",
    "CourseProgress",
    "ModuleProgress",
    "LessonProgress",
    "UserTrainingProfile",
    "LessonStatus",
]
