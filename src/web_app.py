"""
Web Application Entry Point

FastAPI-based web application for the Quiz Application.
Provides REST API endpoints and serves the web frontend.
"""

import sys
import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add src directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_manager import DatabaseManager
from question_manager_db import QuestionManagerDB
from tag_manager_db import TagManagerDB
from quiz_engine import QuizEngine
from analytics import AnalyticsEngine

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global application state
app_controller = None
db_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown."""
    global app_controller, db_manager
    
    # Startup
    logger.info("Starting web application...")
    try:
        # Initialize database manager
        db_path = os.path.join("data", "quiz.db")
        db_manager = DatabaseManager(database_path=db_path, json_data_path="data")
        
        if not db_manager.initialize():
            logger.error("Failed to initialize database")
            raise RuntimeError("Database initialization failed")
        
        # Initialize managers
        question_manager = QuestionManagerDB(db_manager)
        tag_manager = TagManagerDB(db_manager)
        quiz_engine = QuizEngine()
        quiz_engine.question_manager = question_manager
        quiz_engine.tag_manager = tag_manager
        analytics_engine = AnalyticsEngine(db_manager)
        
        app_controller = {
            'question_manager': question_manager,
            'tag_manager': tag_manager,
            'quiz_engine': quiz_engine,
            'analytics_engine': analytics_engine,
            'db_manager': db_manager
        }
        
        logger.info("Web application initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down web application...")
    if db_manager:
        db_manager.close()
    logger.info("Web application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Quiz Application API",
    description="REST API for the Quiz Application",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (frontend)
static_dir = Path(__file__).parent.parent / "web" / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# Pydantic models for request/response
class AnswerModel(BaseModel):
    text: str
    is_correct: bool
    explanation: Optional[str] = None


class QuestionCreate(BaseModel):
    question_text: str = Field(..., min_length=10, max_length=500)
    question_type: str = Field(..., pattern="^(multiple_choice|true_false|select_all|fill_in_blank)$")
    answers: List[AnswerModel] = Field(..., min_items=2, max_items=6)
    tags: List[str] = Field(..., min_items=1, max_items=10)


class QuestionUpdate(BaseModel):
    question_text: Optional[str] = Field(None, min_length=10, max_length=500)
    question_type: Optional[str] = Field(None, pattern="^(multiple_choice|true_false|select_all|fill_in_blank)$")
    answers: Optional[List[AnswerModel]] = Field(None, min_items=2, max_items=6)
    tags: Optional[List[str]] = Field(None, min_items=1, max_items=10)


class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    color: Optional[str] = None
    parent_id: Optional[str] = None
    aliases: Optional[List[str]] = None


class QuizStart(BaseModel):
    num_questions: Optional[int] = Field(10, ge=1, le=100)
    question_types: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    randomize: bool = True


class QuizAnswer(BaseModel):
    question_id: str
    answer_ids: List[str]


# API Routes

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main web page."""
    html_file = Path(__file__).parent.parent / "web" / "index.html"
    if html_file.exists():
        return FileResponse(html_file)
    return HTMLResponse("<h1>Quiz Application API</h1><p>API is running. Frontend not found.</p>")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Quiz Application API is running"}


# Question endpoints

@app.get("/api/questions")
async def get_questions(
    search: Optional[str] = None,
    question_type: Optional[str] = None,
    tags: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """Get all questions with optional filtering."""
    try:
        manager = app_controller['question_manager']
        
        if search or question_type or tags:
            tag_list = tags.split(',') if tags else None
            questions = manager.search_questions(search or "", question_type, tag_list)
        else:
            questions = manager.get_all_questions()
        
        # Apply pagination
        total = len(questions)
        questions = questions[offset:offset + limit]
        
        return {
            "questions": [q.to_dict() if hasattr(q, 'to_dict') else q for q in questions],
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error getting questions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/questions/{question_id}")
async def get_question(question_id: str):
    """Get a specific question by ID."""
    try:
        manager = app_controller['question_manager']
        question = manager.get_question(question_id)
        
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        return question  # Already returns a dict
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/questions")
async def create_question(question: QuestionCreate):
    """Create a new question."""
    try:
        manager = app_controller['question_manager']
        tag_manager = app_controller['tag_manager']
        
        # Convert Pydantic model to dict format
        answers = [{"text": a.text, "is_correct": a.is_correct, "explanation": a.explanation} for a in question.answers]
        
        # Create question
        result = manager.create_question(
            question.question_text,
            question.question_type,
            answers,
            question.tags
        )
        
        if not result:
            raise HTTPException(status_code=400, detail="Failed to create question")
        
        # Ensure tags exist
        for tag_name in question.tags:
            tag = tag_manager.get_tag_by_name(tag_name)
            if not tag:
                tag_manager.create_tag(tag_name)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/questions/{question_id}")
async def update_question(question_id: str, question: QuestionUpdate):
    """Update an existing question."""
    try:
        manager = app_controller['question_manager']
        existing = manager.get_question(question_id)
        
        if not existing:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Convert answers to dict format if provided
        answers = None
        if question.answers is not None:
            answers = [{"text": a.text, "is_correct": a.is_correct, "explanation": a.explanation} for a in question.answers]
        
        # Update question using individual parameters
        success = manager.update_question(
            question_id,
            question_text=question.question_text,
            question_type=question.question_type,
            answers=answers,
            tags=question.tags
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update question")
        
        updated = manager.get_question(question_id)
        return updated
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/questions/{question_id}")
async def delete_question(question_id: str):
    """Delete a question."""
    try:
        manager = app_controller['question_manager']
        success = manager.delete_question(question_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Question not found")
        
        return {"message": "Question deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting question: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Tag endpoints

@app.get("/api/tags")
async def get_tags(search: Optional[str] = None):
    """Get all tags with optional search."""
    try:
        manager = app_controller['tag_manager']
        
        if search:
            tags = manager.search_tags(search)
        else:
            tags = manager.get_all_tags()
        
        return {"tags": tags}
    except Exception as e:
        logger.error(f"Error getting tags: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tags/{tag_id}")
async def get_tag(tag_id: str):
    """Get a specific tag by ID."""
    try:
        manager = app_controller['tag_manager']
        tag = manager.get_tag(tag_id)
        
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")
        
        return tag
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tag: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tags")
async def create_tag(tag: TagCreate):
    """Create a new tag."""
    try:
        manager = app_controller['tag_manager']
        tag_id = manager.create_tag(
            tag.name,
            tag.description,
            tag.color,
            tag.parent_id,
            tag.aliases
        )
        
        if not tag_id:
            raise HTTPException(status_code=400, detail="Failed to create tag")
        
        created = manager.get_tag(tag_id)
        return created
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating tag: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/tags/{tag_id}")
async def delete_tag(tag_id: str):
    """Delete a tag."""
    try:
        manager = app_controller['tag_manager']
        success = manager.delete_tag(tag_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Tag not found")
        
        return {"message": "Tag deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting tag: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Quiz endpoints

@app.post("/api/quiz/start")
async def start_quiz(quiz_config: QuizStart):
    """Start a new quiz session."""
    try:
        engine = app_controller['quiz_engine']
        manager = app_controller['question_manager']
        
        # Get questions based on filters
        if quiz_config.tags:
            questions = manager.get_questions_by_tags(quiz_config.tags)
        else:
            questions = manager.get_all_questions()
        
        # Filter by type if specified
        if quiz_config.question_types:
            questions = [q for q in questions if q.get('question_type') in quiz_config.question_types]
        
        # Randomize and limit number of questions
        if quiz_config.randomize:
            import random
            random.shuffle(questions)
        
        questions = questions[:quiz_config.num_questions]
        
        # Use quiz engine to create randomized quiz
        engine = app_controller['quiz_engine']
        quiz_questions = engine.create_randomized_quiz(questions, len(questions))
        
        # Start quiz session
        session_id = engine.start_quiz(quiz_questions)
        
        if not session_id:
            raise HTTPException(status_code=500, detail="Failed to start quiz session")
        
        return {
            "session_id": session_id,
            "questions": quiz_questions,
            "total_questions": len(quiz_questions)
        }
    except Exception as e:
        logger.error(f"Error starting quiz: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/quiz/submit")
async def submit_quiz_answer(answer: QuizAnswer):
    """Submit an answer for a quiz question."""
    try:
        engine = app_controller['quiz_engine']
        manager = app_controller['question_manager']
        
        question = manager.get_question(answer.question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Score the answer (simplified)
        question_dict = question.to_dict() if hasattr(question, 'to_dict') else question
        correct_answers = [a.get('id') or i for i, a in enumerate(question_dict.get('answers', [])) if a.get('is_correct')]
        
        is_correct = set(answer.answer_ids) == set(str(a) for a in correct_answers)
        
        return {
            "correct": is_correct,
            "correct_answers": correct_answers,
            "user_answers": answer.answer_ids
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting answer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Analytics endpoints

@app.get("/api/analytics/overview")
async def get_analytics_overview():
    """Get analytics overview."""
    try:
        engine = app_controller['analytics_engine']
        stats = engine.get_performance_analytics()
        return stats
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_statistics():
    """Get general statistics."""
    try:
        q_manager = app_controller['question_manager']
        t_manager = app_controller['tag_manager']
        
        questions = q_manager.get_all_questions()
        tags = t_manager.get_all_tags()
        
        return {
            "total_questions": len(questions),
            "total_tags": len(tags),
            "questions_by_type": {}
        }
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

