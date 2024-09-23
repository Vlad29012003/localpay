from typing import Optional

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from exceptions.exceptions import (
    CommentNotFoundException,
    InvalidCommentDataException,
    InvalidPaginationParametersException,
)
from logs.logger_service import LoggerService
from models.comment import Comment
from schemas.comment import CommentCreate, CommentUpdate

log_service = LoggerService("logs/comment_service")
success_logger, error_logger = log_service.configure_loggers("comment_service_success", "comment_service_error")


class CommentService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_comments(self, cursor: Optional[int] = None, per_page: int = 10):

        query = self.db.query(Comment)

        if cursor:
            query = query.filter(Comment.id > cursor)

        try:
            db_comments = query.limit(per_page).all()
            next_cursor = db_comments[-1].id if db_comments else None

            total_count = self.db.query(Comment).count()
            success_logger.info(f"Retrieved {len(db_comments)} comments, total count: {total_count}")
            return db_comments, total_count, next_cursor
        except Exception as e:
            error_logger.error(f"Error fetching comments: {str(e)}")
            raise e

    def get_comment_by_id(self, comment_id: int):
        success_logger.info(f"Fetching comment with ID {comment_id}")

        try:
            comment = self.db.query(Comment).filter(Comment.id == comment_id).first()
            if comment is None:
                error_logger.warning(f"Comment with ID {comment_id} not found")
                raise CommentNotFoundException(comment_id)
            success_logger.info(f"Comment with ID {comment_id} fetched successfully")
            return comment
        except Exception as e:
            error_logger.error(f"Error fetching comment with ID {comment_id}: {str(e)}")
            raise e

    def create_comment(self, comment: CommentCreate):
        success_logger.info(f"Creating new comment for user ID {comment.user_id}")

        try:
            new_comment = Comment(
                user_id=comment.user_id,
                text=comment.text,
                payment_type=comment.payment_type,
                old_available_balance=comment.old_available_balance,
                old_spent_money=comment.old_spent_money,
                add_to_available_balance=comment.add_to_available_balance,
                add_to_spent_money=comment.add_to_spent_money,
                new_available_balance=comment.new_available_balance,
                new_spent_money=comment.new_spent_money
            )

            self.db.add(new_comment)
            self.db.commit()
            self.db.refresh(new_comment)
            success_logger.info(f"New comment created with ID {new_comment.id} for user ID {new_comment.user_id}")
            return new_comment
        except Exception as e:
            error_logger.error(f"Error creating comment for user ID {comment.user_id}: {str(e)}")
            raise e

    def update_comment(self, comment_id: int, comment: CommentUpdate):
        success_logger.info(f"Updating comment with ID {comment_id}")

        try:
            db_comment = self.get_comment_by_id(comment_id)

            if db_comment is None:
                error_logger.warning(f"Comment with ID {comment_id} not found for update")
                raise CommentNotFoundException(comment_id)

            update_data = comment.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(db_comment, field):
                    setattr(db_comment, field, value)
                else:
                    error_logger.error(f"Invalid field: {field}")
                    raise InvalidCommentDataException(f"Invalid field: {field}")

            self.db.commit()
            self.db.refresh(db_comment)
            success_logger.info(f"Comment with ID {comment_id} updated successfully")
            return db_comment
        except Exception as e:
            error_logger.error(f"Error updating comment with ID {comment_id}: {str(e)}")
            raise e

    def delete_comment(self, comment_id: int):
        success_logger.info(f"Deleting comment with ID {comment_id}")

        try:
            comment = self.get_comment_by_id(comment_id)
            self.db.delete(comment)
            self.db.commit()
            success_logger.info(f"Comment with ID {comment_id} deleted successfully")
            return {"status": "success"}
        except Exception as e:
            error_logger.error(f"Error deleting comment with ID {comment_id}: {str(e)}")
            raise e

