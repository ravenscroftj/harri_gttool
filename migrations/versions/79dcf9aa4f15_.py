"""add UserID to article_papers primary key

Revision ID: 79dcf9aa4f15
Revises: 451512b7ee9b
Create Date: 2018-04-03 10:58:52.939561

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '79dcf9aa4f15'
down_revision = '451512b7ee9b'
branch_labels = None
depends_on = None


def upgrade():
    # delete foreign keys
    op.drop_constraint("article_papers_ibfk_1", 'article_papers', type_='foreignkey')
    op.drop_constraint("article_papers_ibfk_2", 'article_papers', type_='foreignkey')
    op.drop_constraint("article_papers_ibfk_3", 'article_papers', type_='foreignkey')

    # change primary key over to new format
    op.execute("ALTER TABLE article_papers DROP PRIMARY KEY")
    op.create_primary_key("pk_article_papers", "article_papers", ["article_id","paper_id","user_id" ])

    #recreate primary keys
    op.create_foreign_key("article_papers_ibfk_1", 'article_papers', 'articles', ['article_id'], ['article_id'])
    op.create_foreign_key("article_papers_ibfk_2", 'article_papers', 'papers', ['paper_id'], ['paper_id'])
    op.create_foreign_key("article_papers_ibfk_3", 'article_papers', 'user', ['user_id'], ['id'])
        


def downgrade():

    # delete foreign keys
    op.drop_constraint("article_papers_ibfk_1", 'article_papers', type_='foreignkey')
    op.drop_constraint("article_papers_ibfk_2", 'article_papers', type_='foreignkey')
    op.drop_constraint("article_papers_ibfk_3", 'article_papers', type_='foreignkey')

    # revert primary key back to the way it was before
    op.execute("ALTER TABLE article_papers DROP PRIMARY KEY")
    op.create_primary_key("pk_article_papers", "article_papers", ["article_id","paper_id"])

    #recreate primary keys
    op.create_foreign_key("article_papers_ibfk_1", 'article_papers', 'article_id', ['article_id'], ['article_id'])
    op.create_foreign_key("article_papers_ibfk_2", 'article_papers', 'papers', ['paper_id'], ['paper_id'])
    op.create_foreign_key("article_papers_ibfk_3", 'article_papers', 'user', ['user_id'], ['id'])
