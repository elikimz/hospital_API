"""Initial migration

Revision ID: ae4eb0b30ba0
Revises: 
Create Date: 2025-02-15 21:05:15.012053

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ae4eb0b30ba0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_users_id', table_name='users')
    op.drop_table('users')
    op.drop_index('ix_reports_id', table_name='reports')
    op.drop_table('reports')
    op.drop_index('ix_appointments_id', table_name='appointments')
    op.drop_table('appointments')
    op.drop_index('ix_staff_id', table_name='staff')
    op.drop_table('staff')
    op.drop_index('ix_prescriptions_id', table_name='prescriptions')
    op.drop_table('prescriptions')
    op.drop_index('ix_patients_id', table_name='patients')
    op.drop_table('patients')
    op.drop_index('ix_payments_id', table_name='payments')
    op.drop_table('payments')
    op.drop_index('ix_medicines_id', table_name='medicines')
    op.drop_table('medicines')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('medicines',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('medicines_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('stock', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('price', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='medicines_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_index('ix_medicines_id', 'medicines', ['id'], unique=False)
    op.create_table('payments',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('patient_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('amount', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.Column('status', postgresql.ENUM('PENDING', 'SUCCESS', 'FAILED', name='paymentstatus'), autoincrement=False, nullable=True),
    sa.Column('method', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('stripe_session_id', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], name='payments_patient_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='payments_pkey')
    )
    op.create_index('ix_payments_id', 'payments', ['id'], unique=False)
    op.create_table('patients',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('patients_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('full_name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('dob', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('contact', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='patients_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='patients_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_index('ix_patients_id', 'patients', ['id'], unique=False)
    op.create_table('prescriptions',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('doctor_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('patient_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('medicine_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('dosage', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['doctor_id'], ['staff.id'], name='prescriptions_doctor_id_fkey'),
    sa.ForeignKeyConstraint(['medicine_id'], ['medicines.id'], name='prescriptions_medicine_id_fkey'),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], name='prescriptions_patient_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='prescriptions_pkey')
    )
    op.create_index('ix_prescriptions_id', 'prescriptions', ['id'], unique=False)
    op.create_table('staff',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('staff_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('full_name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('department', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('contact', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='staff_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='staff_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_index('ix_staff_id', 'staff', ['id'], unique=False)
    op.create_table('appointments',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('patient_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('doctor_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('date', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('duration', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('reason', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('appointment_type', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('status', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('notes', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['doctor_id'], ['staff.id'], name='appointments_doctor_id_fkey'),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], name='appointments_patient_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='appointments_pkey')
    )
    op.create_index('ix_appointments_id', 'appointments', ['id'], unique=False)
    op.create_table('reports',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('report_type', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('details', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='reports_pkey')
    )
    op.create_index('ix_reports_id', 'reports', ['id'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('username', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('email', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('hashed_password', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('role', postgresql.ENUM('ADMIN', 'DOCTOR', 'NURSE', 'RECEPTIONIST', 'PHARMACIST', 'PATIENT', name='userrole_enum'), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='users_pkey'),
    sa.UniqueConstraint('email', name='users_email_key'),
    sa.UniqueConstraint('username', name='users_username_key')
    )
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    # ### end Alembic commands ###
