"""
User progress models for tracking player advancement through mysteries.
Includes game state, achievements, statistics, and save/load functionality.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from uuid import UUID

class ProgressStatus(str, Enum):
    """Possible progress status values."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    PAUSED = "paused"
    ABANDONED = "abandoned"

class AchievementType(str, Enum):
    """Types of achievements players can earn."""
    FIRST_MYSTERY = "first_mystery"
    QUICK_SOLVER = "quick_solver"
    THOROUGH_INVESTIGATOR = "thorough_investigator"
    CLUE_COLLECTOR = "clue_collector"
    MASTER_INTERROGATOR = "master_interrogator"
    PERFECT_DEDUCTION = "perfect_deduction"
    MYSTERY_MARATHON = "mystery_marathon"
    EAGLE_EYE = "eagle_eye"
    PERSISTENCE = "persistence"
    SPEED_DEMON = "speed_demon"

class DifficultyLevel(str, Enum):
    """Difficulty levels for mysteries."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class GameStatistics(BaseModel):
    """Player's overall game statistics."""
    model_config = ConfigDict(extra="ignore")
    
    # Overall progress
    total_mysteries_started: int = 0
    total_mysteries_completed: int = 0
    total_mysteries_abandoned: int = 0
    
    # Time tracking
    total_play_time_minutes: int = 0
    average_completion_time_minutes: Optional[float] = None
    fastest_completion_time_minutes: Optional[int] = None
    
    # Investigation metrics
    total_clues_discovered: int = 0
    total_suspects_questioned: int = 0
    total_actions_taken: int = 0
    total_choices_made: int = 0
    
    # Performance metrics
    correct_deductions: int = 0
    incorrect_deductions: int = 0
    hints_used: int = 0
    perfect_solves: int = 0  # Mysteries solved without hints or wrong deductions
    
    # Difficulty progression
    beginner_mysteries_completed: int = 0
    intermediate_mysteries_completed: int = 0
    advanced_mysteries_completed: int = 0
    expert_mysteries_completed: int = 0
    
    # Streaks
    current_solving_streak: int = 0
    best_solving_streak: int = 0
    current_daily_streak: int = 0
    best_daily_streak: int = 0
    
    # Last activity
    last_played: Optional[datetime] = None
    last_completed_mystery: Optional[datetime] = None

class Achievement(BaseModel):
    """Individual achievement earned by player."""
    model_config = ConfigDict(extra="ignore")
    
    id: str
    type: AchievementType
    name: str
    description: str
    icon: Optional[str] = None
    points: int = 0
    earned_at: datetime
    mystery_id: Optional[str] = None  # If achievement was earned in specific mystery
    
class MysteryProgress(BaseModel):
    """Progress tracking for a specific mystery."""
    model_config = ConfigDict(extra="ignore")
    
    # Basic info
    mystery_id: str
    mystery_title: str
    difficulty: DifficultyLevel
    status: ProgressStatus
    
    # Progress tracking
    current_scene: str = "introduction"
    scenes_completed: List[str] = Field(default_factory=list)
    total_scenes: Optional[int] = None
    progress_percentage: float = 0.0
    
    # Investigation progress
    clues_discovered: List[Dict[str, Any]] = Field(default_factory=list)
    suspects_met: List[str] = Field(default_factory=list)
    suspects_questioned: List[str] = Field(default_factory=list)
    locations_visited: List[str] = Field(default_factory=list)
    
    # Choices and actions
    choices_made: List[Dict[str, Any]] = Field(default_factory=list)
    actions_taken: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Performance metrics
    hints_used: int = 0
    wrong_deductions: int = 0
    investigation_score: Optional[int] = None  # Out of 100
    
    # Timing
    started_at: datetime
    last_played: datetime
    completed_at: Optional[datetime] = None
    time_played_minutes: int = 0
    
    # Save state
    save_data: Dict[str, Any] = Field(default_factory=dict)  # Custom save data
    checkpoint_data: Dict[str, Any] = Field(default_factory=dict)  # Auto-save checkpoints

class UserProgress(BaseModel):
    """Complete user progress tracking."""
    model_config = ConfigDict(extra="ignore")
    
    # User identification
    user_id: str
    username: Optional[str] = None
    
    # Overall statistics
    statistics: GameStatistics = Field(default_factory=GameStatistics)
    
    # Achievements
    achievements: List[Achievement] = Field(default_factory=list)
    achievement_points: int = 0
    
    # Mystery progress
    mystery_progress: Dict[str, MysteryProgress] = Field(default_factory=dict)
    current_mystery_id: Optional[str] = None
    
    # User preferences and settings
    preferences: Dict[str, Any] = Field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_backup: Optional[datetime] = None

# Request/Response Models for API endpoints

class SaveProgressRequest(BaseModel):
    """Request model for saving user progress."""
    model_config = ConfigDict(extra="ignore")
    
    mystery_id: str
    progress_data: Dict[str, Any]
    checkpoint_name: Optional[str] = None
    auto_save: bool = False

class LoadProgressRequest(BaseModel):
    """Request model for loading user progress."""
    model_config = ConfigDict(extra="ignore")
    
    mystery_id: Optional[str] = None  # If None, loads overall progress
    checkpoint_name: Optional[str] = None
    include_statistics: bool = True
    include_achievements: bool = True

class SaveProgressResponse(BaseModel):
    """Response model for save progress operations."""
    model_config = ConfigDict(extra="ignore")
    
    success: bool
    save_id: str
    timestamp: datetime
    mystery_id: str
    checkpoint_name: Optional[str] = None
    backup_created: bool = False

class LoadProgressResponse(BaseModel):
    """Response model for load progress operations."""
    model_config = ConfigDict(extra="ignore")
    
    user_progress: UserProgress
    mystery_progress: Optional[MysteryProgress] = None
    last_save_timestamp: Optional[datetime] = None
    available_checkpoints: List[str] = Field(default_factory=list)

class ProgressSummaryResponse(BaseModel):
    """Response model for progress summary."""
    model_config = ConfigDict(extra="ignore")
    
    user_id: str
    total_mysteries: int
    completed_mysteries: int
    current_mystery: Optional[str] = None
    achievement_count: int
    total_play_time_hours: float
    last_played: Optional[datetime] = None
    progress_level: str  # "Beginner", "Intermediate", "Advanced", "Expert"
    completion_rate: float  # Percentage of started mysteries completed

class BackupProgressRequest(BaseModel):
    """Request model for creating progress backup."""
    model_config = ConfigDict(extra="ignore")
    
    backup_name: Optional[str] = None
    include_save_states: bool = True
    compress: bool = True

class RestoreProgressRequest(BaseModel):
    """Request model for restoring from backup."""
    model_config = ConfigDict(extra="ignore")
    
    backup_id: str
    restore_mysteries: bool = True
    restore_achievements: bool = True
    restore_statistics: bool = True

class ProgressAnalytics(BaseModel):
    """Analytics data for user progress."""
    model_config = ConfigDict(extra="ignore")
    
    user_id: str
    session_count: int
    average_session_duration: float
    favorite_mystery_type: Optional[str] = None
    peak_play_times: List[str] = Field(default_factory=list)
    difficulty_preference: DifficultyLevel
    completion_patterns: Dict[str, Any] = Field(default_factory=dict)
    improvement_metrics: Dict[str, float] = Field(default_factory=dict)

class LeaderboardEntry(BaseModel):
    """Entry for progress leaderboards."""
    model_config = ConfigDict(extra="ignore")
    
    rank: int
    user_id: str
    username: Optional[str] = None
    score: float
    metric_type: str  # "completion_time", "mysteries_solved", "achievement_points", etc.
    value: Union[int, float, str]
    timestamp: datetime

# Error Models

class ProgressError(BaseModel):
    """Error response for progress operations."""
    model_config = ConfigDict(extra="ignore")
    
    error_type: str
    message: str
    mystery_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow) 