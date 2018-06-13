from itertools import groupby


def parameter_sorting(modelInstance):
    parameters = modelInstance.params

    # create a default parameter set if there isn't one yet
    if len(modelInstance.parameter_sets) == 0:
        print ('No parameter sets - creating a default set')
        modelInstance.parameter_sets['ParameterSet_1'] = {}
        for param in parameters:
            modelInstance.parameter_sets['ParameterSet_1'][param] = 0

    evaluated_parameters = modelInstance.evaluated_parameter_sets
    
    subsectionTitles = {
        'input': "Inputs from the 'technosphere'",
        'intermediate': "Inputs from other processes",
        'biosphere': "Direct emissions to the environment"
    }
    
    to_name = lambda x: parameters[x]['to_name']
    input_order = lambda x: parameters[x]['coords'][1]
    type_of = lambda x: parameters[x]['type']

    sorted_keys = sorted(parameters, key=input_order)

    sorted_parameters = []

    for target, items in groupby(sorted_keys, to_name):
        #print(target)
        
        section = {'name': target, 'my_items': []}

        sorted_exchanges = sorted(items, key=type_of)

        #print sorted_exchanges
        for type, exchanges in groupby(sorted_exchanges, type_of):
            #print('\t{}'.format(type))
            subsection = {'name': subsectionTitles[type], 'my_items': []}
            for exchange in exchanges:

                if parameters[exchange].get('function'):
                    #print ('{} determined by a function'.format(exchange))
                    values = ['{} = {:.3g}'.format(parameters[exchange]['function'], e_ps[exchange]) for e_ps_name, e_ps in evaluated_parameters.items()]
                    isFunction = True
                else:
                    values = [ps[exchange] if exchange in ps.keys() else '' for ps_name, ps in modelInstance.parameter_sets.items()]
                    isFunction = False

                #print('\t\t{} ({}) {}'.format(parameters[exchange]['from_name'], exchange, values))

                subsection['my_items'].append({'id': exchange, 'name': parameters[exchange]['from_name'], 'existing_values': values, 'unit': parameters[exchange]['unit'], 'isFunction': isFunction})
            
            section['my_items'].append(subsection)
        
        db_code = (modelInstance.database['name'], parameters[exchange]['to'])
        #print(db_code)
        
        unit = modelInstance.database['items'][db_code]['unit']
        section['name'] = "{}\t(1 {})".format(target, unit)
        sorted_parameters.append(section)

    ext_section = {'name': 'Global Parameters', 'my_items': [{'name': 'User created', 'my_items': []}]}
    for e_p in modelInstance.ext_params:
        values = [ps[e_p['name']] if e_p['name'] in ps.keys() else e_p['default'] for ps_name, ps in modelInstance.parameter_sets.items()]
        ext_section['my_items'][0]['my_items'].append({'id': e_p['name'], 'name': e_p['description'], 'existing_values': values, 'unit': '', 'isFunction': False})

    sorted_parameters.append(ext_section)

    return sorted_parameters
