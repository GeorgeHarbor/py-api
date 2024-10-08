"""add body and tag to tasks

Revision ID: 13bd88504a91
Revises: bdc28367a5e4
Create Date: 2024-09-05 16:31:31.877387

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '13bd88504a91'
down_revision = 'bdc28367a5e4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.add_column(sa.Column('body', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('tag', sa.String(length=36), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.drop_column('tag')
        batch_op.drop_column('body')

    # ### end Alembic commands ###
