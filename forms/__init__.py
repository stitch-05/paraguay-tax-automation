"""Form handlers for Paraguay tax filing."""

from forms.base import FormHandler
from forms.form_211 import Form211Handler
from forms.form_955 import Form955Handler
from forms.registro import RegistroHandler
from forms.porcentajes import PorcentajesHandler

# Map form numbers/names to handler classes
FORM_HANDLERS = {
    '211': Form211Handler,
    '955': Form955Handler,
}

# Map profile update names to handler classes
PROFILE_HANDLERS = {
    'registro_de_contribuyentes': RegistroHandler,
    'porcentajes_actividades': PorcentajesHandler,
}

__all__ = [
    'FormHandler',
    'Form211Handler',
    'Form955Handler',
    'RegistroHandler',
    'PorcentajesHandler',
    'FORM_HANDLERS',
    'PROFILE_HANDLERS',
]
