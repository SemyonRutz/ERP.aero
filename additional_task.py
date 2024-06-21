import pprint, re, pdb


class TableProcessor:
    def __init__(self, table, websocket_response, base_ws):
        """
        Initialize the TableProcessor with the given arguments.
        
        :param table: List of dictionaries containing table data
        :param websocket_response: Dictionary containing websocket response data
        :param base_ws: Dictionary containing base websocket keys
        """
        self.table = table
        self.websocket_response = websocket_response
        self.base_ws = base_ws
        self.my_dict = {}  # Final dictionary to store processed data
        self.list_of_columns = []  # Temporary list to store columns
        self.list_of_columns_with_sort = []  # List to store columns with sort keys
        self.dict_of_order_by = {}  # Dictionary to store order by data
        self.dict_of_conditions_data = {}  # Dictionary to store conditions data

    def process_columns(self):
        """
        Process columns from the table and websocket response, and add them to the final dictionary.
        """
        for row in self.table:
            for key, value in row.items():
                if key == 'Columns View':
                    websocket_in_table = value
                    for websocket_key, websocket_value in self.websocket_response.items():
                        if websocket_in_table == websocket_key:
                            dict_of_columns = websocket_value.copy()
                            if 'filter' in dict_of_columns:
                                del dict_of_columns['filter']  # Remove 'filter' key if present
                            self.list_of_columns.append(dict_of_columns)

        sort_count = 0
        for col in self.list_of_columns:
            col['sort'] = sort_count  # Add sort key
            sort_count += 1
            self.list_of_columns_with_sort.append(col)

        self.my_dict[self.base_ws['Columns View']] = self.list_of_columns_with_sort  # Add to final dictionary

    def process_order_by(self):
        """
        Process order by data from the table and websocket response, and add it to the final dictionary.
        """
        for row in self.table:
            for key, value in row.items():
                if key == 'Columns View':
                    websocket_in_table = value
                if key == 'Sort By' and value != '':
                    order_by_value = value
                    columns_view = row['Columns View']
                    for websocket_key, websocket_value in self.websocket_response.items():
                        if columns_view == websocket_key:
                            dict_of_order_by = websocket_value.copy()
                            if 'filter' in dict_of_order_by:
                                del dict_of_order_by['filter']  # Remove 'filter' key if present
                            dict_of_order_by['direction'] = order_by_value  # Add direction key
                            self.my_dict[self.base_ws['Sort By']] = dict_of_order_by  # Add to final dictionary

    def process_conditions_data(self):
        """
        Process conditions data from the table and websocket response, and add it to the final dictionary.
        """
        dict_of_types_and_values = {}
        client_po_list = []
        so_no_list = []

        for row in self.table:
            for key, value in row.items():
                if key == 'Columns View':
                    websocket_in_table = value
                if key == 'Condition' and value != '':
                    conditions_data_value = value
                    columns_view = row['Columns View']
                    for websocket_key, websocket_value in self.websocket_response.items():
                        if columns_view == websocket_key:
                            web_socket_dict = websocket_value
                            if conditions_data_value != '' and web_socket_dict['filter'] == 'so_no':
                                split_values = re.split(',|=', conditions_data_value)
                                for i in range(0, len(split_values), 2):
                                    dict_of_types_and_values = {'type': split_values[i], 'value': split_values[i + 1]}
                                    so_no_list.append(dict_of_types_and_values)
                                self.dict_of_conditions_data[web_socket_dict['filter']] = so_no_list
                            elif conditions_data_value != '' and web_socket_dict['filter'] == 'client_po':
                                split_values = re.split(',|=', conditions_data_value)
                                for i in range(0, len(split_values), 2):
                                    dict_of_types_and_values = {'type': split_values[i], 'value': split_values[i + 1]}
                                    client_po_list.append(dict_of_types_and_values)
                                self.dict_of_conditions_data[web_socket_dict['filter']] = client_po_list

        self.my_dict[self.base_ws['Condition']] = self.dict_of_conditions_data  # Add to final dictionary

    def process_page_and_row(self):
        """
        Process page size and row height from the table, and add them to the final dictionary.
        """
        for row in self.table:
            for key, value in row.items():
                if key == 'Lines per page' and value != '':
                    page_size = value
                    self.my_dict[self.base_ws['Lines per page']] = page_size  # Add page size to final dictionary
                if key == 'Row Height' and value != '':
                    row_height = value
                    self.my_dict[self.base_ws['Row Height']] = row_height  # Add row height to final dictionary

        self.my_dict['module'] = 'SO'  # Add static module key

    def process_all(self):
        """
        Process all data and add it to the final dictionary.
        """
        self.process_columns()
        self.process_order_by()
        self.process_conditions_data()
        self.process_page_and_row()


table = [{'Columns View': 'SO Number', 'Sort By': '', 'Highlight By': 'equals=S110=rgba(172,86,86,1),equals=S111', 'Condition': 'equals=S110,equals=S111', 'Row Height': '60', 'Lines per page': '25'},
         {'Columns View': 'Client PO', 'Sort By': '', 'Highlight By': 'equals=P110,equals=P111', 'Condition': 'equals=P110', 'Row Height': '', 'Lines per page': ''},
         {'Columns View': 'Terms of Sale', 'Sort By': 'asc', 'Highlight By': 'equals=S110=rgba(172,86,86,1)', 'Condition': '', 'Row Height': '', 'Lines per page': ''}]

websocket_response = {'Client PO': {'index': 'so_list_client_po', 'filter': 'client_po'},
                      'SO Number': {'index': 'so_list_so_number', 'filter': 'so_no'},
                      'Terms of Sale': {'index': 'so_list_terms_of_sale', 'filter': 'term_sale'}}

base_ws = {'Columns View': 'columns',
           'Sort By': 'order_by',
           'Condition': 'conditions_data',
           'Lines per page': 'page_size',
           'Row Height': 'row_height',
           'Highlight By': 'color_conditions'}






processor = TableProcessor(table, websocket_response, base_ws)
processor.process_all()

pprint.pprint(processor.my_dict) # Output the final dictionary

                            
                            


#################################################### OUTPUT ####################################################


result = {'columns': [{'index': 'so_list_so_number', 'sort': 0}, 
                      {'index': 'so_list_client_po', 'sort': 1}, 
                      {'index': 'so_list_terms_of_sale', 'sort': 2}], 
          'order_by': {'direction': 'asc', 'index': 'so_list_terms_of_sale'},
          'conditions_data': {'so_no': [{'type': 'equals', 'value': 'S110'}, 
                                        {'type': 'equals', 'value': 'S111'}], 
                              'client_po': [{'type': 'equals', 'value': 'P110'}]}, 
          'page_size': '25', 
          'row_height': '60',
          'color_conditions': {'so_no': [{'type': 'equals', 'value': 'S110', 'color': 'rgba(172,86,86,1)'}], 
                               'client_po': [{'type': 'equals', 'value': 'S110', 'color': ''}, {'type': 'equals', 'value': 'S111', 'color': ''}],
                               'term_sale': []}, 
          'module': 'SO'}
