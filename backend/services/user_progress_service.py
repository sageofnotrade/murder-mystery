"""
UserProgressService for managing user progress, achievements, and save/load functionality.
Integrates with Supabase for persistence and existing story/mystery services.
"""

from typing import Dict, List, Optional, Any
import uuid
import json
import logging
from datetime import datetime, timedelta
from supabase import Client
from models.user_progress_models import (
    UserProgress, MysteryProgress, GameStatistics, Achievement,
    ProgressStatus, AchievementType, DifficultyLevel,
    SaveProgressRequest, LoadProgressRequest, SaveProgressResponse, LoadProgressResponse,
    ProgressSummaryResponse, ProgressAnalytics, BackupProgressRequest
)

logger = logging.getLogger(__name__)

class UserProgressService:
    """Service for handling user progress operations."""
    
    def __init__(self, supabase_client: Client):
        self.supabase = supabase_client
    
    async def get_user_progress(self, user_id: str, include_mystery_details: bool = True) -> UserProgress:
        """Get complete user progress."""
        try:
            # Get main user progress record
            progress_response = self.supabase.table('user_progress').select('*').eq('user_id', user_id).execute()
            
            if not progress_response.data:
                # Create new progress record if doesn't exist
                return await self.create_user_progress(user_id)
            
            progress_data = progress_response.data[0]
            
            # Parse JSON fields
            statistics = GameStatistics(**json.loads(progress_data.get('statistics', '{}')))
            achievements = [Achievement(**a) for a in json.loads(progress_data.get('achievements', '[]'))]
            preferences = json.loads(progress_data.get('preferences', '{}'))
            
            # Get mystery progress if requested
            mystery_progress = {}
            if include_mystery_details:
                mystery_response = self.supabase.table('mystery_progress').select('*').eq('user_id', user_id).execute()
                
                for mystery_data in mystery_response.data:
                    mystery_progress[mystery_data['mystery_id']] = MysteryProgress(
                        mystery_id=mystery_data['mystery_id'],
                        mystery_title=mystery_data['mystery_title'],
                        difficulty=DifficultyLevel(mystery_data['difficulty']),
                        status=ProgressStatus(mystery_data['status']),
                        current_scene=mystery_data['current_scene'],
                        scenes_completed=json.loads(mystery_data.get('scenes_completed', '[]')),
                        total_scenes=mystery_data.get('total_scenes'),
                        progress_percentage=mystery_data['progress_percentage'],
                        clues_discovered=json.loads(mystery_data.get('clues_discovered', '[]')),
                        suspects_met=json.loads(mystery_data.get('suspects_met', '[]')),
                        suspects_questioned=json.loads(mystery_data.get('suspects_questioned', '[]')),
                        locations_visited=json.loads(mystery_data.get('locations_visited', '[]')),
                        choices_made=json.loads(mystery_data.get('choices_made', '[]')),
                        actions_taken=json.loads(mystery_data.get('actions_taken', '[]')),
                        hints_used=mystery_data['hints_used'],
                        wrong_deductions=mystery_data['wrong_deductions'],
                        investigation_score=mystery_data.get('investigation_score'),
                        started_at=datetime.fromisoformat(mystery_data['started_at']),
                        last_played=datetime.fromisoformat(mystery_data['last_played']),
                        completed_at=datetime.fromisoformat(mystery_data['completed_at']) if mystery_data.get('completed_at') else None,
                        time_played_minutes=mystery_data['time_played_minutes'],
                        save_data=json.loads(mystery_data.get('save_data', '{}')),
                        checkpoint_data=json.loads(mystery_data.get('checkpoint_data', '{}'))
                    )
            
            return UserProgress(
                user_id=user_id,
                username=progress_data.get('username'),
                statistics=statistics,
                achievements=achievements,
                achievement_points=progress_data['achievement_points'],
                mystery_progress=mystery_progress,
                current_mystery_id=progress_data.get('current_mystery_id'),
                preferences=preferences,
                created_at=datetime.fromisoformat(progress_data['created_at']),
                updated_at=datetime.fromisoformat(progress_data['updated_at']),
                last_backup=datetime.fromisoformat(progress_data['last_backup']) if progress_data.get('last_backup') else None
            )
            
        except Exception as e:
            logger.error(f"Error getting user progress for {user_id}: {str(e)}")
            raise

    async def create_user_progress(self, user_id: str, username: Optional[str] = None) -> UserProgress:
        """Create new user progress record."""
        try:
            now = datetime.utcnow()
            
            progress = UserProgress(
                user_id=user_id,
                username=username,
                created_at=now,
                updated_at=now
            )
            
            # Insert into database
            progress_record = {
                'user_id': user_id,
                'username': username,
                'statistics': json.dumps(progress.statistics.model_dump()),
                'achievements': json.dumps([]),
                'achievement_points': 0,
                'current_mystery_id': None,
                'preferences': json.dumps({}),
                'created_at': now.isoformat(),
                'updated_at': now.isoformat(),
                'last_backup': None
            }
            
            self.supabase.table('user_progress').insert(progress_record).execute()
            
            return progress
            
        except Exception as e:
            logger.error(f"Error creating user progress for {user_id}: {str(e)}")
            raise

    async def save_progress(self, user_id: str, request: SaveProgressRequest) -> SaveProgressResponse:
        """Save user progress for a specific mystery."""
        try:
            save_id = str(uuid.uuid4())
            timestamp = datetime.utcnow()
            
            # Get current mystery progress or create new
            mystery_progress = await self.get_mystery_progress(user_id, request.mystery_id)
            
            if not mystery_progress:
                # Create new mystery progress
                mystery_progress = await self.create_mystery_progress(user_id, request.mystery_id)
            
            # Update progress data
            mystery_progress.save_data.update(request.progress_data)
            mystery_progress.last_played = timestamp
            
            # Handle checkpoints
            if request.checkpoint_name:
                mystery_progress.checkpoint_data[request.checkpoint_name] = {
                    'save_id': save_id,
                    'timestamp': timestamp.isoformat(),
                    'data': request.progress_data
                }
            
            # Auto-save checkpoint
            if request.auto_save:
                mystery_progress.checkpoint_data['auto_save'] = {
                    'save_id': save_id,
                    'timestamp': timestamp.isoformat(),
                    'data': request.progress_data
                }
            
            # Update in database
            await self.update_mystery_progress(mystery_progress)
            
            # Update user's overall progress
            await self.update_user_last_played(user_id, timestamp)
            
            return SaveProgressResponse(
                success=True,
                save_id=save_id,
                timestamp=timestamp,
                mystery_id=request.mystery_id,
                checkpoint_name=request.checkpoint_name,
                backup_created=False  # TODO: Implement backup logic
            )
            
        except Exception as e:
            logger.error(f"Error saving progress for user {user_id}: {str(e)}")
            raise

    async def load_progress(self, user_id: str, request: LoadProgressRequest) -> LoadProgressResponse:
        """Load user progress."""
        try:
            # Get overall user progress
            user_progress = await self.get_user_progress(user_id, include_mystery_details=False)
            
            mystery_progress = None
            available_checkpoints = []
            last_save_timestamp = None
            
            # Get specific mystery progress if requested
            if request.mystery_id:
                mystery_progress = await self.get_mystery_progress(user_id, request.mystery_id)
                
                if mystery_progress:
                    # Get available checkpoints
                    available_checkpoints = list(mystery_progress.checkpoint_data.keys())
                    
                    # Get last save timestamp
                    if mystery_progress.checkpoint_data:
                        timestamps = [
                            datetime.fromisoformat(cp['timestamp']) 
                            for cp in mystery_progress.checkpoint_data.values()
                            if 'timestamp' in cp
                        ]
                        if timestamps:
                            last_save_timestamp = max(timestamps)
                    
                    # Load specific checkpoint if requested
                    if request.checkpoint_name and request.checkpoint_name in mystery_progress.checkpoint_data:
                        checkpoint_data = mystery_progress.checkpoint_data[request.checkpoint_name]
                        mystery_progress.save_data = checkpoint_data.get('data', {})
            
            return LoadProgressResponse(
                user_progress=user_progress,
                mystery_progress=mystery_progress,
                last_save_timestamp=last_save_timestamp,
                available_checkpoints=available_checkpoints
            )
            
        except Exception as e:
            logger.error(f"Error loading progress for user {user_id}: {str(e)}")
            raise

    async def get_mystery_progress(self, user_id: str, mystery_id: str) -> Optional[MysteryProgress]:
        """Get progress for a specific mystery."""
        try:
            response = self.supabase.table('mystery_progress').select('*').eq('user_id', user_id).eq('mystery_id', mystery_id).execute()
            
            if not response.data:
                return None
            
            data = response.data[0]
            
            return MysteryProgress(
                mystery_id=data['mystery_id'],
                mystery_title=data['mystery_title'],
                difficulty=DifficultyLevel(data['difficulty']),
                status=ProgressStatus(data['status']),
                current_scene=data['current_scene'],
                scenes_completed=json.loads(data.get('scenes_completed', '[]')),
                total_scenes=data.get('total_scenes'),
                progress_percentage=data['progress_percentage'],
                clues_discovered=json.loads(data.get('clues_discovered', '[]')),
                suspects_met=json.loads(data.get('suspects_met', '[]')),
                suspects_questioned=json.loads(data.get('suspects_questioned', '[]')),
                locations_visited=json.loads(data.get('locations_visited', '[]')),
                choices_made=json.loads(data.get('choices_made', '[]')),
                actions_taken=json.loads(data.get('actions_taken', '[]')),
                hints_used=data['hints_used'],
                wrong_deductions=data['wrong_deductions'],
                investigation_score=data.get('investigation_score'),
                started_at=datetime.fromisoformat(data['started_at']),
                last_played=datetime.fromisoformat(data['last_played']),
                completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
                time_played_minutes=data['time_played_minutes'],
                save_data=json.loads(data.get('save_data', '{}')),
                checkpoint_data=json.loads(data.get('checkpoint_data', '{}'))
            )
            
        except Exception as e:
            logger.error(f"Error getting mystery progress for {user_id}, mystery {mystery_id}: {str(e)}")
            raise

    async def create_mystery_progress(self, user_id: str, mystery_id: str) -> MysteryProgress:
        """Create new mystery progress record."""
        try:
            # Get mystery details
            mystery_response = self.supabase.table('mysteries').select('title, difficulty').eq('id', mystery_id).execute()
            
            if not mystery_response.data:
                raise ValueError(f"Mystery {mystery_id} not found")
            
            mystery_data = mystery_response.data[0]
            now = datetime.utcnow()
            
            progress = MysteryProgress(
                mystery_id=mystery_id,
                mystery_title=mystery_data.get('title', 'Unknown Mystery'),
                difficulty=DifficultyLevel(mystery_data.get('difficulty', 'beginner')),
                status=ProgressStatus.IN_PROGRESS,
                started_at=now,
                last_played=now
            )
            
            # Insert into database
            progress_record = {
                'user_id': user_id,
                'mystery_id': mystery_id,
                'mystery_title': progress.mystery_title,
                'difficulty': progress.difficulty.value,
                'status': progress.status.value,
                'current_scene': progress.current_scene,
                'scenes_completed': json.dumps(progress.scenes_completed),
                'total_scenes': progress.total_scenes,
                'progress_percentage': progress.progress_percentage,
                'clues_discovered': json.dumps(progress.clues_discovered),
                'suspects_met': json.dumps(progress.suspects_met),
                'suspects_questioned': json.dumps(progress.suspects_questioned),
                'locations_visited': json.dumps(progress.locations_visited),
                'choices_made': json.dumps(progress.choices_made),
                'actions_taken': json.dumps(progress.actions_taken),
                'hints_used': progress.hints_used,
                'wrong_deductions': progress.wrong_deductions,
                'investigation_score': progress.investigation_score,
                'started_at': progress.started_at.isoformat(),
                'last_played': progress.last_played.isoformat(),
                'completed_at': None,
                'time_played_minutes': progress.time_played_minutes,
                'save_data': json.dumps(progress.save_data),
                'checkpoint_data': json.dumps(progress.checkpoint_data)
            }
            
            self.supabase.table('mystery_progress').insert(progress_record).execute()
            
            # Update user's current mystery
            await self.update_current_mystery(user_id, mystery_id)
            
            return progress
            
        except Exception as e:
            logger.error(f"Error creating mystery progress for {user_id}, mystery {mystery_id}: {str(e)}")
            raise

    async def update_mystery_progress(self, progress: MysteryProgress) -> None:
        """Update mystery progress in database."""
        try:
            update_data = {
                'status': progress.status.value,
                'current_scene': progress.current_scene,
                'scenes_completed': json.dumps(progress.scenes_completed),
                'progress_percentage': progress.progress_percentage,
                'clues_discovered': json.dumps(progress.clues_discovered),
                'suspects_met': json.dumps(progress.suspects_met),
                'suspects_questioned': json.dumps(progress.suspects_questioned),
                'locations_visited': json.dumps(progress.locations_visited),
                'choices_made': json.dumps(progress.choices_made),
                'actions_taken': json.dumps(progress.actions_taken),
                'hints_used': progress.hints_used,
                'wrong_deductions': progress.wrong_deductions,
                'investigation_score': progress.investigation_score,
                'last_played': progress.last_played.isoformat(),
                'completed_at': progress.completed_at.isoformat() if progress.completed_at else None,
                'time_played_minutes': progress.time_played_minutes,
                'save_data': json.dumps(progress.save_data),
                'checkpoint_data': json.dumps(progress.checkpoint_data)
            }
            
            self.supabase.table('mystery_progress').update(update_data).eq('mystery_id', progress.mystery_id).execute()
            
        except Exception as e:
            logger.error(f"Error updating mystery progress for {progress.mystery_id}: {str(e)}")
            raise

    async def get_progress_summary(self, user_id: str) -> ProgressSummaryResponse:
        """Get summary of user's progress."""
        try:
            user_progress = await self.get_user_progress(user_id)
            
            # Calculate derived metrics
            total_mysteries = len(user_progress.mystery_progress)
            completed_mysteries = sum(1 for p in user_progress.mystery_progress.values() if p.status == ProgressStatus.COMPLETED)
            completion_rate = (completed_mysteries / total_mysteries * 100) if total_mysteries > 0 else 0
            total_play_time_hours = user_progress.statistics.total_play_time_minutes / 60
            
            # Determine progress level
            progress_level = "Beginner"
            if completed_mysteries >= 10:
                progress_level = "Expert"
            elif completed_mysteries >= 5:
                progress_level = "Advanced"
            elif completed_mysteries >= 2:
                progress_level = "Intermediate"
            
            return ProgressSummaryResponse(
                user_id=user_id,
                total_mysteries=total_mysteries,
                completed_mysteries=completed_mysteries,
                current_mystery=user_progress.current_mystery_id,
                achievement_count=len(user_progress.achievements),
                total_play_time_hours=total_play_time_hours,
                last_played=user_progress.statistics.last_played,
                progress_level=progress_level,
                completion_rate=completion_rate
            )
            
        except Exception as e:
            logger.error(f"Error getting progress summary for {user_id}: {str(e)}")
            raise

    async def award_achievement(self, user_id: str, achievement_type: AchievementType, mystery_id: Optional[str] = None) -> Achievement:
        """Award an achievement to the user."""
        try:
            # Check if user already has this achievement
            user_progress = await self.get_user_progress(user_id, include_mystery_details=False)
            
            existing_achievement = next((a for a in user_progress.achievements if a.type == achievement_type), None)
            if existing_achievement:
                return existing_achievement
            
            # Create new achievement
            achievement_data = self._get_achievement_data(achievement_type)
            achievement = Achievement(
                id=str(uuid.uuid4()),
                type=achievement_type,
                name=achievement_data['name'],
                description=achievement_data['description'],
                icon=achievement_data.get('icon'),
                points=achievement_data['points'],
                earned_at=datetime.utcnow(),
                mystery_id=mystery_id
            )
            
            # Update user progress
            user_progress.achievements.append(achievement)
            user_progress.achievement_points += achievement.points
            
            # Save to database
            await self.update_user_achievements(user_id, user_progress.achievements, user_progress.achievement_points)
            
            return achievement
            
        except Exception as e:
            logger.error(f"Error awarding achievement {achievement_type} to {user_id}: {str(e)}")
            raise

    async def update_current_mystery(self, user_id: str, mystery_id: str) -> None:
        """Update the user's current mystery."""
        try:
            self.supabase.table('user_progress').update({
                'current_mystery_id': mystery_id,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('user_id', user_id).execute()
            
        except Exception as e:
            logger.error(f"Error updating current mystery for {user_id}: {str(e)}")
            raise

    async def update_user_last_played(self, user_id: str, timestamp: datetime) -> None:
        """Update the user's last played timestamp."""
        try:
            # Get current statistics
            user_progress = await self.get_user_progress(user_id, include_mystery_details=False)
            user_progress.statistics.last_played = timestamp
            
            # Update in database
            self.supabase.table('user_progress').update({
                'statistics': json.dumps(user_progress.statistics.model_dump()),
                'updated_at': timestamp.isoformat()
            }).eq('user_id', user_id).execute()
            
        except Exception as e:
            logger.error(f"Error updating last played for {user_id}: {str(e)}")
            raise

    async def update_user_achievements(self, user_id: str, achievements: List[Achievement], total_points: int) -> None:
        """Update user achievements in database."""
        try:
            achievements_data = [achievement.model_dump() for achievement in achievements]
            
            self.supabase.table('user_progress').update({
                'achievements': json.dumps(achievements_data),
                'achievement_points': total_points,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('user_id', user_id).execute()
            
        except Exception as e:
            logger.error(f"Error updating achievements for {user_id}: {str(e)}")
            raise

    def _get_achievement_data(self, achievement_type: AchievementType) -> Dict[str, Any]:
        """Get achievement data for a specific type."""
        achievement_data = {
            AchievementType.FIRST_MYSTERY: {
                'name': 'First Case Closed',
                'description': 'Complete your first mystery',
                'points': 100,
                'icon': '🏆'
            },
            AchievementType.QUICK_SOLVER: {
                'name': 'Speed Detective',
                'description': 'Solve a mystery in under 30 minutes',
                'points': 200,
                'icon': '⚡'
            },
            AchievementType.THOROUGH_INVESTIGATOR: {
                'name': 'Thorough Investigator',
                'description': 'Discover all clues in a mystery',
                'points': 150,
                'icon': '🔍'
            },
            AchievementType.CLUE_COLLECTOR: {
                'name': 'Clue Collector',
                'description': 'Discover 50 clues across all mysteries',
                'points': 300,
                'icon': '📋'
            },
            AchievementType.MASTER_INTERROGATOR: {
                'name': 'Master Interrogator',
                'description': 'Question all suspects in a mystery',
                'points': 175,
                'icon': '🗣️'
            },
            AchievementType.PERFECT_DEDUCTION: {
                'name': 'Perfect Deduction',
                'description': 'Solve a mystery without any wrong guesses',
                'points': 250,
                'icon': '🎯'
            },
            AchievementType.MYSTERY_MARATHON: {
                'name': 'Mystery Marathon',
                'description': 'Complete 10 mysteries',
                'points': 500,
                'icon': '🏃'
            },
            AchievementType.EAGLE_EYE: {
                'name': 'Eagle Eye',
                'description': 'Find a hidden clue',
                'points': 125,
                'icon': '👁️'
            },
            AchievementType.PERSISTENCE: {
                'name': 'Persistent Detective',
                'description': 'Play for 5 consecutive days',
                'points': 300,
                'icon': '📅'
            },
            AchievementType.SPEED_DEMON: {
                'name': 'Speed Demon',
                'description': 'Complete 3 mysteries in one day',
                'points': 400,
                'icon': '🔥'
            }
        }
        
        return achievement_data.get(achievement_type, {
            'name': 'Unknown Achievement',
            'description': 'A mysterious achievement',
            'points': 0
        }) 