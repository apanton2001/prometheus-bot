"""initial

Revision ID: 20240320000000
Revises: 
Create Date: 2024-03-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20240320000000'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE userrole AS ENUM ('admin', 'trader', 'viewer')")
    op.execute("CREATE TYPE tradetype AS ENUM ('buy', 'sell')")
    op.execute("CREATE TYPE positionstatus AS ENUM ('open', 'closed', 'pending')")
    
    # Create user table
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('role', postgresql.ENUM('admin', 'trader', 'viewer', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_id'), 'user', ['id'], unique=False)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    
    # Create position table
    op.create_table(
        'position',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(), nullable=False),
        sa.Column('entry_price', sa.Float(), nullable=False),
        sa.Column('current_price', sa.Float(), nullable=False),
        sa.Column('size', sa.Float(), nullable=False),
        sa.Column('stop_loss', sa.Float(), nullable=True),
        sa.Column('take_profit', sa.Float(), nullable=True),
        sa.Column('status', postgresql.ENUM('open', 'closed', 'pending', name='positionstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_position_id'), 'position', ['id'], unique=False)
    
    # Create trade table
    op.create_table(
        'trade',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('position_id', sa.Integer(), nullable=False),
        sa.Column('type', postgresql.ENUM('buy', 'sell', name='tradetype'), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('size', sa.Float(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['position_id'], ['position.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_trade_id'), 'trade', ['id'], unique=False)
    
    # Create performance metrics table
    op.create_table(
        'performancemetrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('total_trades', sa.Integer(), nullable=False),
        sa.Column('winning_trades', sa.Integer(), nullable=False),
        sa.Column('losing_trades', sa.Integer(), nullable=False),
        sa.Column('win_rate', sa.Float(), nullable=False),
        sa.Column('total_pnl', sa.Float(), nullable=False),
        sa.Column('average_pnl', sa.Float(), nullable=False),
        sa.Column('max_win', sa.Float(), nullable=False),
        sa.Column('max_loss', sa.Float(), nullable=False),
        sa.Column('profit_factor', sa.Float(), nullable=False),
        sa.Column('sharpe_ratio', sa.Float(), nullable=False),
        sa.Column('period_start', sa.DateTime(), nullable=False),
        sa.Column('period_end', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_performancemetrics_id'), 'performancemetrics', ['id'], unique=False)

def downgrade() -> None:
    # Drop tables
    op.drop_index(op.f('ix_performancemetrics_id'), table_name='performancemetrics')
    op.drop_table('performancemetrics')
    
    op.drop_index(op.f('ix_trade_id'), table_name='trade')
    op.drop_table('trade')
    
    op.drop_index(op.f('ix_position_id'), table_name='position')
    op.drop_table('position')
    
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_index(op.f('ix_user_id'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    
    # Drop enum types
    op.execute("DROP TYPE positionstatus")
    op.execute("DROP TYPE tradetype")
    op.execute("DROP TYPE userrole") 