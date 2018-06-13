import pickle


class LcoptModelView(object):
    """
    This is the base model class.

    To create a new model, enter a name e.g. ``model = LcoptModel('My_Model')``

    To load an existing model use the ``load`` option e.g. ``model = LcoptModel(load = 'My_Model')``

    """

    def __init__(self, load):
        super(LcoptModelView, self).__init__()
        
        self.load(load)
                    
    def load(self, filename):
        """load data from a saved .lcopt file"""
        if filename[-10:] != ".lcoptview":
            filename += ".lcoptview"

        load_data = pickle.load(open("{}".format(filename), "rb"))
        
        attributes = ['name',
                      'database',
                      'params',
                      'ext_params',
                      'names',
                      'parameter_sets',
                      'external_databases',
                      'parameter_map',
                      'sandbox_positions',
                      'ecoinventName',
                      'biosphereName',
                      'analysis_settings',
                      'technosphere_databases',
                      'biosphere_databases',
                      'result_set',
                      'matrix',
                      'evaluated_parameter_sets'
                      ]

        for attr in attributes:
            setattr(self, attr, load_data[attr])
