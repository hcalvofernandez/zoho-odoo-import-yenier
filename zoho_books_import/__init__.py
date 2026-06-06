from . import models
from . import wizard
from . import controllers


def post_init_hook(env):
    """Backfill schema drift when the code is newer than the database."""
    env.cr.execute(
        """
        ALTER TABLE product_template
        ADD COLUMN IF NOT EXISTS zoho_product_type varchar
        """
    )
