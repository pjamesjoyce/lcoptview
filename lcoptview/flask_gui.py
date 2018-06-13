from .modelview import LcoptModelView
from .parameters import parameter_sorting
from .excel_functions import create_excel_summary, create_excel_method
from collections import OrderedDict
from flask import Flask, send_file, request, render_template, session
import json


def uc_first(string):
    return string[0].upper() + string[1:]


app = Flask(__name__)
app.config.from_pyfile('app.cfg')
app.jinja_env.filters['uc_first'] = uc_first  


def shutdown_server():                             # pragma: no cover
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


def load_viewfile(filename):
    return LcoptModelView(filename)


def get_sandbox_variables(filename):

    m = load_viewfile(filename)
    db = m.database['items']
    matrix = m.matrix
    ext_dbs = [x['name'] for x in m.external_databases]
    
    #print (ext_dbs)
    
    def output_code(process_id):
        
        exchanges = m.database['items'][process_id]['exchanges']
        
        production_filter = lambda x: x['type'] == 'production'
           
        code = list(filter(production_filter, exchanges))[0]['input'][1]
        
        return code

    sandbox_positions = m.sandbox_positions

    products = OrderedDict((k, v) for k, v in db.items() if v['type'] == 'product')
    product_codes = [k[1] for k in products.keys()]

    processes = OrderedDict((k, v) for k, v in db.items() if v['type'] == 'process')
    process_codes = [k[1] for k in processes.keys()]
    process_name_map = {k[1]: v['name'] for k, v in processes.items()}

    # note this maps from output code to process
    process_output_map = {output_code(x): x[1] for x in processes.keys()}
    reverse_process_output_map = {value: key for key, value in process_output_map.items()}

    intermediates = {k: v for k, v in products.items() if v['lcopt_type'] == 'intermediate'}
    intermediate_codes = [k[1] for k in intermediates.keys()]
    intermediate_map = {k[1]: v['name'] for k, v in intermediates.items()}

    #process_output_name_map = {process_code: output_name for x in processes.keys()}
    process_output_name_map = {x[1]: intermediate_map[reverse_process_output_map[x[1]]] for x in processes.keys()}

    inputs = OrderedDict((k, v) for k, v in products.items() if v['lcopt_type'] == 'input')
    input_codes = [k[1] for k in inputs.keys()]
    input_map = {k[1]: v['name'] for k, v in inputs.items()}
    #reverse_input_map = {value: key for key, value in input_map.items()}

    biosphere = OrderedDict((k, v) for k, v in products.items() if v['lcopt_type'] == 'biosphere')
    biosphere_codes = [k[1] for k in biosphere.keys()]
    biosphere_map = {k[1]: v['name'] for k, v in biosphere.items()}
    #reverse_biosphere_map = {value: key for key, value in biosphere_map.items()}

    label_map = dict(input_map, **process_output_name_map)
    label_map = dict(label_map, **biosphere_map)
    #label_map = input_map.update(process_output_name_map)
    #label_map = label_map.update(biosphere_map)
    #print (label_map)

    #print('label_map = {}\n'.format(label_map))
    
    outputlabels = [{'process_id': x, 'output_name': process_output_name_map[x]} for x in process_codes]
    
    link_indices = [process_output_map[x] if x in intermediate_codes else x for x in product_codes]
           
    if matrix is not None:
        # TODO: edit this to list of lists 
        row_totals = [sum(a) for a in matrix]
        input_row_totals = {k: row_totals[m.names.index(v)] for k, v in input_map.items()}
        biosphere_row_totals = {k: row_totals[m.names.index(v)] for k, v in biosphere_map.items()}
    
    # compute the nodes
    i = 1
    nodes = []
    for t in process_codes:
        nodes.append({'name': process_name_map[t], 'type': 'transformation', 'id': t, 'initX': i * 100, 'initY': i * 100})
        i += 1
    
    i = 1
    for p in input_codes:
        if input_row_totals[p] != 0:
            item = db[(m.database['name'], p)]
            el = item.get('ext_link')
            if el:
                ext_db_ix = ext_dbs.index(el[0])
                ext_db_items = m.external_databases[ext_db_ix]['items']
                ext_item = ext_db_items[el]
                ext_item_data = "<div><b>Database: </b>{}</br><b>Reference product: </b>{}</br><b>Process: </b>{}</br><b>Location: </b>{}</br></div>".format(el[0], ext_item['reference product'], ext_item['name'], ext_item['location'])
            else:
                ext_item_data = "<div><i><b>This is a burden free input</b></i></div>"
            #ext_items = m.ext
            #print(ext_item_data)
            nodes.append({'name': input_map[p], 'type': 'input', 'id': p + "__0", 'initX': i * 50 + 150, 'initY': i * 50, 'ext_item_data': ext_item_data})
            i += 1

    i = 1
    for p in biosphere_codes:
        if biosphere_row_totals[p] != 0:
            item = db[(m.database['name'], p)]
            el = item.get('ext_link')
            if el:
                ext_db_ix = ext_dbs.index(el[0])
                ext_db_items = m.external_databases[ext_db_ix]['items']
                ext_item = ext_db_items[el]
                if type(ext_item['categories']) == tuple:
                    ext_categories = "; ".join(ext_item['categories'])
                else:
                    ext_categories = ext_item['categories']

                ext_item_data = "<div><b>Database: </b>{}</br><b>Name: </b>{}</br><b>Type: </b>{}</br><b>Categories: </b>{}</br></div>".format(el[0], ext_item['name'], ext_item['type'], ext_categories)
            else:
                ext_item_data = None
            #ext_items = m.ext
            #print(item['name'], el, ext_item_data)
            nodes.append({'name': biosphere_map[p], 'type': 'biosphere', 'id': p + "__0", 'initX': i * 50 + 150, 'initY': i * 50, 'ext_item_data': ext_item_data})
            i += 1
   
    # compute links
    links = []
    
    input_duplicates = []
    biosphere_duplicates = []
    
    #check there is a matrix (new models won't have one until parameter_scan() is run)
    if matrix is not None:

        columns = list(map(list, zip(*matrix)))  # transpose the matrix

        for c, column in enumerate(columns):
            for r, i in enumerate(column):
                if i > 0:
                    p_from = link_indices[r]
                    p_to = link_indices[c]
                    if p_from in input_codes:
                        suffix = "__" + str(input_duplicates.count(p_from))
                        input_duplicates.append(p_from)
                        p_type = 'input'
                    elif p_from in biosphere_codes:
                        suffix = "__" + str(biosphere_duplicates.count(p_from))
                        biosphere_duplicates.append(p_from)
                        p_type = 'biosphere'
                    else:
                        suffix = ""
                        p_type = 'intermediate'
                    
                    links.append({'sourceID': p_from + suffix, 'targetID': p_to, 'type': p_type, 'amount': 1, 'label': label_map[p_from]})
           
    #add extra nodes
    while len(input_duplicates) > 0:
        p = input_duplicates.pop()
        count = input_duplicates.count(p)
        if count > 0:
            suffix = "__" + str(count)
            ext_item_data = [x['ext_item_data'] for x in nodes if x['id'] == p + "__0"][0]
            nodes.append({'name': input_map[p], 'type': 'input', 'id': p + suffix, 'initX': i * 50 + 150, 'initY': i * 50, 'ext_item_data': ext_item_data})
            i += 1
            
    while len(biosphere_duplicates) > 0:
        p = biosphere_duplicates.pop()
        count = biosphere_duplicates.count(p)
        if count > 0:
            suffix = "__" + str(count)
            ext_item_data = [x['ext_item_data'] for x in nodes if x['id'] == p + "__0"][0]
            nodes.append({'name': biosphere_map[p], 'type': 'biosphere', 'id': p + suffix, 'initX': i * 50 + 150, 'initY': i * 50, 'ext_item_data': ext_item_data})
            i += 1
            
    #try and reset the locations
    
    for n in nodes:
        node_id = n['id']
        if node_id in sandbox_positions:
            n['initX'] = sandbox_positions[node_id]['x']
            n['initY'] = sandbox_positions[node_id]['y']
            
    #print(nodes)
    #print(inputs)
    #print(process_name_map)
    return m.name, nodes, links, outputlabels


@app.route('/results.json')
def include_results():
    filename = app.config['CURRENT_FILE']
    modelview = load_viewfile(filename)
    return json.dumps(modelview.result_set)


@app.route('/excel_export')
def excel_export():

    filename = app.config['CURRENT_FILE']
    modelview = load_viewfile(filename)

    export_type = request.args.get('type')
    ps = int(request.args.get('ps'))
    m = int(request.args.get('m'))

    print (export_type, ps, m)

    if export_type == 'summary':

        output = create_excel_summary(modelview)

        filename = "{}_summary_results.xlsx".format(modelview.name)

    elif export_type == 'method':

        output = create_excel_method(modelview, m)

        filename = "{}_{}_results.xlsx".format(modelview.name, modelview.result_set['settings']['method_names'][m])

    #finally return the file
    return send_file(output, attachment_filename=filename, as_attachment=True)


@app.route('/')
@app.route('/index')
def view_model():

    filename = app.config['CURRENT_FILE']
    modelview = load_viewfile(filename)
    name, nodes, links, outputlabels = get_sandbox_variables(filename)

    args = {'model': {'name': name}, 'nodes': nodes, 'links': links, 'outputlabels': outputlabels}

    if modelview.result_set is not None:

        item = modelview.result_set['settings']['item']

        args['item'] = item
        args['result_sets'] = modelview.result_set
       
    sorted_parameters = parameter_sorting(modelview)

    args['sorted_parameters'] = sorted_parameters
    args['ps_names'] = [x for x in modelview.parameter_sets.keys()]

    return render_template('model_page.html', args=args)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


@app.route('/shutdown')
def shutdown():                             # pragma: no cover
    shutdown_server()
    return render_template('shutdown.html')


@app.route('/test')
def test():
    return render_template('test.html')
