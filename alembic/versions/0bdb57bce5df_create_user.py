"""create-user

Revision ID: 0bdb57bce5df
Revises: 53067b2b4230
Create Date: 2021-10-05 10:14:39.269819

"""
import os

from alembic import op
from sqlalchemy import orm

from database.models import User
from settings import settings

# revision identifiers, used by Alembic.
revision = "0bdb57bce5df"
down_revision = "53067b2b4230"
branch_labels = None
depends_on = "53067b2b4230"


def upgrade():
    bind = op.get_bind()
    session = orm.Session(bind=bind)
    hashed_password = User.encode_password(settings.SEED_USER_PASSWORD)
    seed_user = User(name=settings.SEED_USER_NAME, password=hashed_password)
    session.add(seed_user)
    session.commit()
    session.close()


def downgrade():
    bind = op.get_bind()
    session = orm.Session(bind=bind)
    session.query(User).filter_by(name=settings.SEED_USER_NAME).delete()
    session.commit()
    session.close()
