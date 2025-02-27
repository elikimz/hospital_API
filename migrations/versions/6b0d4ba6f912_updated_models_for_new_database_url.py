"""Updated models for new database URL

Revision ID: 6b0d4ba6f912
Revises: c0b46d61ac39
Create Date: 2025-02-27 16:24:55.830518

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6b0d4ba6f912'
down_revision: Union[str, None] = 'c0b46d61ac39'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_medical_history_id', table_name='medical_history')
    op.drop_table('medical_history')
    op.drop_index('ix_audit_logs_id', table_name='audit_logs')
    op.drop_table('audit_logs')
    op.drop_column('medicines', 'batch_number')
    op.drop_column('medicines', 'expiry_date')
    op.drop_column('medicines', 'manufacturer')
    op.drop_column('patients', 'gender')
    op.drop_column('patients', 'address')
    op.drop_column('patients', 'emergency_contact')
    op.drop_column('payments', 'transaction_id')
    op.drop_column('payments', 'payment_date')
    op.drop_column('prescriptions', 'frequency')
    op.drop_column('prescriptions', 'instructions')
    op.alter_column('reports', 'details',
               existing_type=sa.TEXT(),
               type_=sa.String(),
               existing_nullable=False)
    op.drop_column('staff', 'title')
    op.drop_column('staff', 'specialization')
    op.drop_column('staff', 'qualifications')
    op.drop_column('users', 'phone_number')
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'last_name')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('last_name', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('first_name', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('phone_number', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('staff', sa.Column('qualifications', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('staff', sa.Column('specialization', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('staff', sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.alter_column('reports', 'details',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=False)
    op.add_column('prescriptions', sa.Column('instructions', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('prescriptions', sa.Column('frequency', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('payments', sa.Column('payment_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('payments', sa.Column('transaction_id', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('patients', sa.Column('emergency_contact', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('patients', sa.Column('address', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('patients', sa.Column('gender', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('medicines', sa.Column('manufacturer', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('medicines', sa.Column('expiry_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('medicines', sa.Column('batch_number', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.create_table('audit_logs',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('action', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('details', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='audit_logs_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='audit_logs_pkey')
    )
    op.create_index('ix_audit_logs_id', 'audit_logs', ['id'], unique=False)
    op.create_table('medical_history',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('patient_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('details', sa.TEXT(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], name='medical_history_patient_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='medical_history_pkey')
    )
    op.create_index('ix_medical_history_id', 'medical_history', ['id'], unique=False)
    # ### end Alembic commands ###
