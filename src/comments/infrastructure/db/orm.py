from sqlalchemy import Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.comments.domain.entities import Comment
from src.db.base import Base


class CommentsOrm(Base):
    __tablename__ = "comments"

    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["UsersOrm"] = relationship(back_populates="comments", lazy="joined")
    content: Mapped[str] = mapped_column(Text(length=250), nullable=False)

    def to_entity(self):
        return Comment(
            game_id=self.game_id,
            user_id=self.user_id,
            user=self.user.email,
            content=self.content
        )
