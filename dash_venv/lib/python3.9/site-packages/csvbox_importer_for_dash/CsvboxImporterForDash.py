# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class CsvboxImporterForDash(Component):
    """A CsvboxImporterForDash component.
CsvboxImporterForDash is a component for CSVBox.io integration in Dash.

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- data (dict; optional):
    Data from the import operation.

- licenseKey (string; required):
    The license key for CSVBox.io.

- result (boolean; optional):
    Result of the import operation.

- userId (string; required):
    The user ID for CSVBox.io."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'csvbox_importer_for_dash'
    _type = 'CsvboxImporterForDash'
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, licenseKey=Component.REQUIRED, userId=Component.REQUIRED, result=Component.UNDEFINED, data=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'data', 'licenseKey', 'result', 'userId']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'data', 'licenseKey', 'result', 'userId']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        for k in ['licenseKey', 'userId']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(CsvboxImporterForDash, self).__init__(**args)
