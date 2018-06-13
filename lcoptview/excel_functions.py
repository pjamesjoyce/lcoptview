from io import BytesIO
import xlsxwriter


def create_excel_summary(modelInstance):

    settings = modelInstance.result_set['settings']
    results = modelInstance.result_set['results']

    method_names = ['{}{}'.format(x[0].upper(), x[1:]) for x in settings['method_names']]
    ps_names = settings['ps_names']

    #create an output stream
    output = BytesIO()

    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    base_format = {'border': 1, 'align': 'center'}
    base_header_format = {'border': 1, 'align': 'center', 'bold': True, 'text_wrap': True}

    cell_format = workbook.add_format(base_format)
    cell_format.set_align('vcenter')

    row_header_format = workbook.add_format(base_header_format)
    row_header_format.set_align('vcenter')
    
    col_header_format = workbook.add_format(base_header_format)
    col_header_format.set_align('vcenter')

    title_format = workbook.add_format({'bold': True, 'font_size': 20})
    
    row_offset = 2
    col_offset = 1

    worksheet.write(row_offset, col_offset, 'Impact', col_header_format)
    worksheet.write(row_offset, col_offset + 1, 'Unit', col_header_format)

    worksheet.write(0, 1, '{} summary'.format(modelInstance.name), title_format)

    for i, m in enumerate(method_names):
        for j, p in enumerate(ps_names):
            worksheet.write(i + row_offset + 1, j + col_offset + 2, results[j][i]['score'], cell_format)

    for i, m in enumerate(method_names):
        worksheet.write(i + row_offset + 1, col_offset, m, row_header_format)
        worksheet.write(i + row_offset + 1, col_offset + 1, settings['method_units'][i], row_header_format)

    for j, p in enumerate(ps_names):
        worksheet.write(row_offset, j + col_offset + 2, p, col_header_format)

    start_col, end_col = xlsxwriter.utility.xl_col_to_name(0), xlsxwriter.utility.xl_col_to_name(0)
    worksheet.set_column('{}:{}'.format(start_col, end_col), 5)

    start_col, end_col = xlsxwriter.utility.xl_col_to_name(col_offset), xlsxwriter.utility.xl_col_to_name(col_offset)
    worksheet.set_column('{}:{}'.format(start_col, end_col), 25)

    start_col, end_col = xlsxwriter.utility.xl_col_to_name(col_offset + 1), xlsxwriter.utility.xl_col_to_name(col_offset + 1 + len(ps_names))
    worksheet.set_column('{}:{}'.format(start_col, end_col), 12)

    workbook.close()

    #go back to the beginning of the stream
    output.seek(0)
    
    return output
    

def create_excel_method(modelInstance, m):
    
    settings = modelInstance.result_set['settings']
    results = modelInstance.result_set['results']

    method_names = ['{}{}'.format(x[0].upper(), x[1:]) for x in settings['method_names']]

    method = method_names[m]

    ps_names = settings['ps_names']

    table_data = []

    for i, p in enumerate(ps_names):
        foreground_results = results[i][m]['foreground_results']
        this_item = []

        for k, v in foreground_results.items():

            running_total = 0

            for j, _ in enumerate(ps_names):
                running_total += abs(results[j][m]['foreground_results'][k])

            if(running_total != 0):
                this_item.append({'name': k, 'value': v, 'rt': running_total})

        this_item = sorted(this_item, key=lambda x: x['rt'], reverse=True)

        table_data.append(this_item)

    #print(table_data)
    
    output = BytesIO()

    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    base_format = {'border': 1, 'align': 'center'}
    base_header_format = {'border': 1, 'align': 'center', 'bold': True, 'text_wrap': True}

    cell_format = workbook.add_format(base_format)
    cell_format.set_align('vcenter')

    total_format = workbook.add_format(base_header_format)
    total_format.set_align('vcenter')
    total_format.set_bg_color('#eeeeee')

    row_header_format = workbook.add_format(base_header_format)
    row_header_format.set_align('vcenter')
    
    col_header_format = workbook.add_format(base_header_format)
    col_header_format.set_align('vcenter')

    title_format = workbook.add_format({'bold': True, 'font_size': 12})

    row_offset = 4
    col_offset = 1

    worksheet.write(0, 1, 'Model', title_format)
    worksheet.write(0, 2, modelInstance.name, title_format)

    worksheet.write(1, 1, 'Method', title_format)
    worksheet.write(1, 2, method, title_format)

    worksheet.write(2, 1, 'Unit', title_format)
    worksheet.write(2, 2, settings['method_units'][m], title_format)

    worksheet.write(row_offset, col_offset, 'Process', col_header_format)
    worksheet.write(row_offset + 1, col_offset, 'Total', total_format)

    for i, p in enumerate(ps_names):
        worksheet.write(row_offset, col_offset + i + 1, p, col_header_format)
        worksheet.write(row_offset + 1, col_offset + i + 1, results[i][m]['score'], total_format)

    for i, item in enumerate(table_data[0]):
        worksheet.write(row_offset + i + 2, col_offset, item['name'], row_header_format)

    no_items = len(table_data[0])

    for i, item in enumerate(table_data):
        for j in range(no_items):
            worksheet.write(row_offset + j + 2, col_offset + i + 1, item[j]['value'], cell_format)
    
    start_col, end_col = xlsxwriter.utility.xl_col_to_name(0), xlsxwriter.utility.xl_col_to_name(0)
    worksheet.set_column('{}:{}'.format(start_col, end_col), 5)

    start_col, end_col = xlsxwriter.utility.xl_col_to_name(col_offset), xlsxwriter.utility.xl_col_to_name(col_offset)
    worksheet.set_column('{}:{}'.format(start_col, end_col), 25)

    start_col, end_col = xlsxwriter.utility.xl_col_to_name(col_offset + 1), xlsxwriter.utility.xl_col_to_name(col_offset + len(ps_names))
    worksheet.set_column('{}:{}'.format(start_col, end_col), 12)

    workbook.close()
    output.seek(0)

    return output