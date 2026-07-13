"""sincronizar esquema con modelos actuales

Revision ID: a1b2c3d4e5f6
Revises: 7f9e3b1c4d5a
Create Date: 2026-07-13 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '7f9e3b1c4d5a'
branch_labels = None
depends_on = None


def upgrade():
    # --- matriculas: add comprobante_path ---
    op.add_column('matriculas', sa.Column('comprobante_path', sa.String(length=255), nullable=True))

    # --- seccion_horarios: add aula and estado ---
    op.add_column('seccion_horarios', sa.Column('aula', sa.String(length=100), nullable=True))
    op.add_column('seccion_horarios', sa.Column('estado', sa.String(length=20), nullable=True, server_default='Activo'))

    # --- seccion_docentes: add horas_asignadas ---
    op.add_column('seccion_docentes', sa.Column('horas_asignadas', sa.SmallInteger(), nullable=True))

    # --- plan_estudiantes: add semestre_id ---
    op.add_column('plan_estudiantes', sa.Column('semestre_id', sa.Integer(), sa.ForeignKey('semestres.id'), nullable=True))

    # --- certificados: remove autorizado and emitido (replaced by estado field) ---
    op.drop_column('certificados', 'autorizado')
    op.drop_column('certificados', 'emitido')


def downgrade():
    # --- certificados: restore removed columns ---
    op.add_column('certificados', sa.Column('emitido', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('certificados', sa.Column('autorizado', sa.Boolean(), nullable=False, server_default='0'))

    # --- plan_estudiantes: drop semestre_id ---
    op.drop_column('plan_estudiantes', 'semestre_id')

    # --- seccion_docentes: drop horas_asignadas ---
    op.drop_column('seccion_docentes', 'horas_asignadas')

    # --- seccion_horarios: drop aula and estado ---
    op.drop_column('seccion_horarios', 'estado')
    op.drop_column('seccion_horarios', 'aula')

    # --- matriculas: drop comprobante_path ---
    op.drop_column('matriculas', 'comprobante_path')
