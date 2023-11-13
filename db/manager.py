from db import get_connection
from db.fields import Column
import db.models 


class Manager:
    select_cols = []
    foreign_keys = {}
    many_to_many = {}

    def execute_query(self, query, *args):
        connection = get_connection()
        self.cursor = connection.cursor()
        self.cursor.execute(query, args)
        connection.commit()
        res = self.cursor.fetchall()
        connection.close()
        return res

    def fetch_records(self, query, *args):
        result_set = self.execute_query(query, *args)
        queryset = []

        # Dictionary to store unique instances based on their primary key (id)
        db_dict = {}

        for row in result_set:
            # Create a dictionary from the row, mapping column names to values
            instance_data = {column_name: value for column_name, value in zip(self.select_cols, row)}

            # Extract the primary key value (id) from the instance data
            id_value = instance_data.get(f'{self.Klass.db.table_name}.id')

            # Initialize an entry in the dictionary if the primary key is not present
            if id_value not in db_dict:
                db_dict[id_value] = {col_name: [] for col_name in self.many_to_many}

            # Update the dictionary with the instance data
            db_dict[id_value].update(instance_data)

            # Process many-to-many fields
            for col_name, m2m_field in self.many_to_many.items():
                m2m_model = m2m_field.model  # Get the many-to-many related model (e.g., Classroom)
                nested_instance_data = {}

                # Extract values for columns in the related model
                for nested_column_name in m2m_model.db.cols:
                    nested_key = f'{m2m_model.db.table_name}.{nested_column_name}'
                    m2m_value = db_dict[id_value].pop(nested_key, None)
                    nested_instance_data[nested_column_name] = m2m_value

                # Append a new instance of the related model to the list
                if nested_instance_data.get('id') is not None:
                    db_dict[id_value][m2m_field.name].append(m2m_model(**nested_instance_data))

            # Process foreign key fields
            for col_name, foreign_key in self.foreign_keys.items():
                foreign_model = foreign_key.model
                nested_instance_data = {}

                # Extract values for columns in the related model
                for nested_column_name in foreign_model.db.cols:
                    nested_key = f'{foreign_model.db.table_name}.{nested_column_name}'
                    nested_instance_data[nested_column_name] = db_dict[id_value].pop(nested_key, None)

                # Create an instance of the related model and assign it to the foreign key field
                db_dict[id_value][foreign_key.name] = foreign_model(**nested_instance_data)

        # Convert the dictionary values to a list of instances
        queryset = [self.Klass(**instance_data) for instance_data in db_dict.values()]

        return queryset

    def dispatch_fields(self):
        select_cols, foreign_keys, many_to_many = [], {}, {}
        # Iterate over columns to check for foreign keys        
        for col_name, col_instance in self.fields.items():
            if isinstance(col_instance, Column):
                if col_instance.constraint == 'fkey':
                    model  = col_instance.model
                    for fname, finstance in model.db.fields.items():
                        if finstance.constraint != 'm2m' and finstance.constraint != 'fkey':
                            select_cols.append(f'{model.db.table_name}.{fname}')

                        # repeat the same loop
                    col_instance.name = col_name
                    foreign_keys[col_name] = col_instance
                elif col_instance.constraint == 'm2m':
                    model  = col_instance.model
                    for fname, finstance in model.db.fields.items():
                        if finstance.constraint != 'm2m' and finstance.constraint != 'fkey':
                            select_cols.append(f'{model.db.table_name}.{fname}')
                    col_instance.name = col_name 
                    many_to_many[col_name] = col_instance
                else:
                    select_cols.append(f'{self.table_name}.{col_name}')

        return select_cols, foreign_keys, many_to_many

    def all(self, order_by=None, reverse=False):
        # Generate the SELECT part of the query with foreign keys
        order = "DESC" if reverse else "ASC"
        order_clause = f"ORDER BY {order_by} {order}" if order_by else ""

        self.select_cols, self.foreign_keys, self.many_to_many = self.dispatch_fields()

        query = f"SELECT {', '.join(self.select_cols)} FROM {self.table_name}"

        # Join tables for foreign keys
        for col_name, fk_field in self.foreign_keys.items():
            query += f" LEFT JOIN {fk_field.model.db.table_name} ON {self.table_name}.{fk_field.name}_id = {fk_field.model.db.table_name}.id"

        # Join tables for foreign keys
        for col_name, m2m_field in self.many_to_many.items():
            through_model = m2m_field.through_model
            if isinstance(through_model, str):
                through_model = getattr(db.models, through_model)

            through_table_name = through_model.db.table_name

            reverse_field_1 = None 
            reverse_field_2 = None 
            for field_name, field in through_model.db.fields.items():
                if field.constraint == 'fkey' and field.model == self.Klass:
                    reverse_field_1 = field_name
                elif field.constraint == 'fkey' and field.model == m2m_field.model:
                    reverse_field_2 = field_name

            query += f" LEFT OUTER JOIN {through_table_name} ON {self.table_name}.id = {through_table_name}.{reverse_field_1}_id"
            query += f" LEFT OUTER JOIN {m2m_field.model.db.table_name} ON {through_table_name}.{reverse_field_2}_id = {m2m_field.model.db.table_name}.id"

            # SELECT * FROM teachers LEFT OUTER JOIN teacher_classrooms ON teachers.id == teacher_classrooms.teacher_id

        query += f" {order_clause}"

        return self.fetch_records(query)

    def filter(self, **kwargs):
        # Validate search_cols to avoid SQL injection
        self.select_cols, self.foreign_keys, self.many_to_many = self.dispatch_fields()

        conditions = " AND ".join([f"{key} = ?" for key in kwargs])
        
        query = f"SELECT {','.join(self.select_cols)} FROM {self.table_name}"

        # Join tables for foreign keys
        for col_name, fk_field in self.foreign_keys.items():
            query += f" LEFT JOIN {fk_field.model.db.table_name} ON {self.table_name}.{fk_field.name}_id = {fk_field.model.db.table_name}.id"


        # Join tables for foreign keys
        for col_name, m2m_field in self.many_to_many.items():
            through_model = m2m_field.through_model
            if isinstance(through_model, str):
                through_model = getattr(db.models, through_model)

            through_table_name = through_model.db.table_name

            reverse_field_1 = None 
            reverse_field_2 = None 
            for field_name, field in through_model.db.fields.items():
                if field.constraint == 'fkey' and field.model == self.Klass:
                    reverse_field_1 = field_name
                elif field.constraint == 'fkey' and field.model == m2m_field.model:
                    reverse_field_2 = field_name

            query += f" LEFT OUTER JOIN {through_table_name} ON {self.table_name}.id = {through_table_name}.{reverse_field_1}_id"
            query += f" LEFT OUTER JOIN {m2m_field.model.db.table_name} ON {through_table_name}.{reverse_field_2}_id = {m2m_field.model.db.table_name}.id"

            # SELECT * FROM teachers LEFT OUTER JOIN teacher_classrooms ON teachers.id == teacher_classrooms.teacher_id


        query += f' WHERE {conditions}'

        values = list(kwargs.values())

        return self.fetch_records(query, *values)

    def search(self, keyword, search_cols=['id']):
        # Validate search_cols to avoid SQL injection
        self.select_cols, self.foreign_keys, self.many_to_many = self.dispatch_fields()

        valid_search_cols = []
        for col in search_cols:
            if '.' in col:
                field_name, nested_field_name = col.split('.')
                fk_field = self.foreign_keys[field_name]
                col = f'{fk_field.model.db.table_name}.{nested_field_name}'
            else:
                col = f'{self.table_name}.{col}'

            if col in self.select_cols:
                valid_search_cols.append(col)

        # Construct the WHERE clause based on the provided columns
        conditions = " OR ".join([f"{col} LIKE ?" for col in valid_search_cols])

        if not conditions:
            return []

        query = f"SELECT {','.join(self.select_cols)} FROM {self.table_name}"

        # Join tables for foreign keys
        for col_name, fk_field in self.foreign_keys.items():
            query += f" LEFT JOIN {fk_field.model.db.table_name} ON {self.table_name}.{fk_field.name}_id = {fk_field.model.db.table_name}.id"

        # Join tables for foreign keys
        for col_name, m2m_field in self.many_to_many.items():
            through_model = m2m_field.through_model
            if isinstance(through_model, str):
                through_model = getattr(db.models, through_model)

            through_table_name = through_model.db.table_name

            reverse_field_1 = None 
            reverse_field_2 = None 
            for field_name, field in through_model.db.fields.items():
                if field.constraint == 'fkey' and field.model == self.Klass:
                    reverse_field_1 = field_name
                elif field.constraint == 'fkey' and field.model == m2m_field.model:
                    reverse_field_2 = field_name

            query += f" LEFT OUTER JOIN {through_table_name} ON {self.table_name}.id = {through_table_name}.{reverse_field_1}_id"
            query += f" LEFT OUTER JOIN {m2m_field.model.db.table_name} ON {through_table_name}.{reverse_field_2}_id = {m2m_field.model.db.table_name}.id"

            # SELECT * FROM teachers LEFT OUTER JOIN teacher_classrooms ON teachers.id == teacher_classrooms.teacher_id


        query += f' WHERE {conditions}'

        keyword_pattern = f"%{keyword}%"

        values = [keyword_pattern] * len(valid_search_cols)

        return self.fetch_records(query, *values)

    def get(self, **kwargs):
        self.select_cols, self.foreign_keys, self.many_to_many = self.dispatch_fields()

        conditions = " AND ".join([f"{key} = ?" for key in kwargs])
        values = list(kwargs.values())
        query = f"SELECT {','.join(self.select_cols)} FROM {self.table_name}"
        
        # Join tables for foreign keys
        for col_name, fk_field in self.foreign_keys.items():
            query += f" LEFT JOIN {fk_field.model.db.table_name} ON {self.table_name}.{fk_field.name}_id = {fk_field.model.db.table_name}.id"

        # Join tables for foreign keys
        for col_name, m2m_field in self.many_to_many.items():
            through_model = m2m_field.through_model
            if isinstance(through_model, str):
                through_model = getattr(db.models, through_model)

            through_table_name = through_model.db.table_name

            reverse_field_1 = None 
            reverse_field_2 = None 
            for field_name, field in through_model.db.fields.items():
                if field.constraint == 'fkey' and field.model == self.Klass:
                    reverse_field_1 = field_name
                elif field.constraint == 'fkey' and field.model == m2m_field.model:
                    reverse_field_2 = field_name

            query += f" LEFT OUTER JOIN {through_table_name} ON {self.table_name}.id = {through_table_name}.{reverse_field_1}_id"
            query += f" LEFT OUTER JOIN {m2m_field.model.db.table_name} ON {through_table_name}.{reverse_field_2}_id = {m2m_field.model.db.table_name}.id"

            # SELECT * FROM teachers LEFT OUTER JOIN teacher_classrooms ON teachers.id == teacher_classrooms.teacher_id


        query += f' WHERE {conditions} LIMIT 1'

        res = self.execute_query(query, *values)

        if not res:
            return None
        frow = {colname: value for colname, value in zip(self.select_cols, res[0])}
        return self.Klass(**frow)

    def delete(self, **kwargs):
        conditions = " AND ".join([f"{key} = ?" for key in kwargs])
        values = list(kwargs.values())
        query = f"DELETE FROM {self.table_name}"
        if conditions:
            query += f' WHERE {conditions}'

        print('query', query)
        self.execute_query(query, *values)

    def bulk_delete(self, id_list):
        if not id_list and id_list != '*all':
            print("No IDs provided for bulk deletion.")
            return

        query = f"DELETE FROM {self.table_name}"
        if isinstance(id_list, list) or isinstance(id_list, tuple):
            conditions = "id IN ({})".format(", ".join("?" for _ in id_list))
            query += f' WHERE {conditions}'
            self.execute_query(query, *id_list)
        else:
            self.execute_query(query)

    def update(self, filter_kwargs, update_kwargs):
        self.select_cols, self.foreign_keys, self.many_to_many = self.dispatch_fields()
        
        '''db.update({'id': 1}, {'name': 12})'''
        filter_conditions = " AND ".join([f"{key} = ?" for key in filter_kwargs])
        filter_values = list(filter_kwargs.values())

        keys_to_remove = []
        to_add_kwargs = {}
        for col, value in update_kwargs.items():
            if col in self.foreign_keys and not col.endswith('_id'):
                to_add_kwargs[f'{col}_id'] = kwargs.get(col).id
                keys_to_remove.append(col)

            elif col in self.many_to_many:
                keys_to_remove.append(col)

        update_kwargs.update(to_add_kwargs)
        # remove unnecessary keys
        [update_kwargs.pop(key) for key in keys_to_remove]

        update_columns = ", ".join([f"{key} = ?" for key in update_kwargs])
        update_values = list(update_kwargs.values())
        query = f"UPDATE {self.table_name} SET {update_columns} WHERE {filter_conditions}"
        self.execute_query(query, *(update_values + filter_values))

    def create(self, response=True, **kwargs):
        # Extract foreign key fields and their values
        self.select_cols, self.foreign_keys, self.many_to_many = self.dispatch_fields()

        keys_to_remove = []
        to_add_kwargs = {}
        for col, value in kwargs.items():
            if col in self.foreign_keys and not col.endswith('_id'):
                to_add_kwargs[f'{col}_id'] = kwargs.get(col).id
                keys_to_remove.append(col)

            elif col in self.many_to_many:
                keys_to_remove.append(col)

        kwargs.update(to_add_kwargs)
        # remove unnecessary keys
        [kwargs.pop(key) for key in keys_to_remove]

        columns = ', '.join(kwargs.keys())

        placeholders = ', '.join(['?'] * len(kwargs))
        values = list(kwargs.values())
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        self.execute_query(query, *values)

        
        if response:
            # Retrieve the last inserted rowid
            last_rowid = self.cursor.lastrowid

            # Fetch the last inserted row
            query_last_row = f"SELECT {', '.join(self.select_cols)} FROM {self.table_name}"

            # Join tables for foreign keys
            for col_name, fk_field in self.foreign_keys.items():
                query_last_row += f" LEFT JOIN {fk_field.model.db.table_name} ON {self.table_name}.{fk_field.name}_id = {fk_field.model.db.table_name}.id"

            # Join tables for foreign keys
            for col_name, m2m_field in self.many_to_many.items():
                through_model = m2m_field.through_model
                if isinstance(through_model, str):
                    through_model = getattr(db.models, through_model)

                through_table_name = through_model.db.table_name

                reverse_field_1 = None 
                reverse_field_2 = None 
                for field_name, field in through_model.db.fields.items():
                    if field.constraint == 'fkey' and field.model == self.Klass:
                        reverse_field_1 = field_name
                    elif field.constraint == 'fkey' and field.model == m2m_field.model:
                        reverse_field_2 = field_name

                query_last_row += f" LEFT OUTER JOIN {through_table_name} ON {self.table_name}.id = {through_table_name}.{reverse_field_1}_id"
                query_last_row += f" LEFT OUTER JOIN {m2m_field.model.db.table_name} ON {through_table_name}.{reverse_field_2}_id = {m2m_field.model.db.table_name}.id"

                # SELECT * FROM teachers LEFT OUTER JOIN teacher_classrooms ON teachers.id == teacher_classrooms.teacher_id


            query_last_row += f' WHERE {self.table_name}.id = ?'

            last_row = self.execute_query(query_last_row, last_rowid)

            # Check if the last row is not empty
            if last_row:
                # Assuming fetch_records returns a dictionary representing the row
                frow = {colname: value for colname, value in zip(self.select_cols, last_row[0])}

                # Add foreign key instances to the row
                for col_name, foreign_key in self.foreign_keys.items():
                    foreign_model = foreign_key.model
                    nested_instance_data = {}

                    for nested_column_name in foreign_model.db.cols:
                        nested_key = f'{foreign_model.db.table_name}.{nested_column_name}'
                        nested_instance_data[nested_column_name] = frow.pop(nested_key, None)

                    frow[foreign_key.name] = foreign_model(**nested_instance_data)

                # Create and return an instance of Klass with the columns set

                return self.Klass(**frow)
        return None

    def first(self, order_by='id', reverse=False):
        order = "DESC" if reverse else "ASC"
        query = f"SELECT {','.join(self.cols)} FROM {self.table_name} ORDER BY {order_by} {order} LIMIT 1"
        res = self.execute_query(query)
        if not res:
            return None
        frow = {colname: value for colname, value in zip(self.cols, res[0])}
        return self.Klass(**frow)

    def last(self, order_by='id', reverse=False):
        order = "ASC" if reverse else "DESC"
        query = f"SELECT {','.join(self.cols)} FROM {self.table_name} ORDER BY {order_by} {order} LIMIT 1"
        res = self.execute_query(query)
        if not res:
            return None
        frow = {colname: value for colname, value in zip(self.cols, res[0])}
        return self.Klass(**frow)

class ModelBaseMeta(type):
    def __init__(cls, name, bases, attrs):
        super(ModelBaseMeta, cls).__init__(name, bases, attrs)
        
        # Initialize the db attribute as a Manager instance
        cls.db = Manager()

        attribute_names = {key: value for key, value in attrs.items() if not key.startswith('__') and key != 'Props'}
        
        # Collect column names for the table from the class attributes
        cls.db.cols = attribute_names.keys()
        
        # Set the table name from the Props attribute if it exists
        if 'Props' in attrs:
            cls.fields = attribute_names
            cls.db.fields = attribute_names
            cls.db.Klass = cls
            cls.db.table_name = attrs['Props'].table_name

class ModelBase(metaclass=ModelBaseMeta):
    def __init__(self, *args, **kwargs):
        if not hasattr(self.Props, "table_name"):
            raise AttributeError("Props.table_name is not defined.")

        # self.fields = self.__class__.fields

        for field_name in kwargs:
            if '.' in field_name:
                table_name, col_name = field_name.split('.')
            else:
                col_name = field_name

            if col_name in self.__class__.db.cols:
                setattr(self, col_name, kwargs.get(field_name))

        # for col in kwargs:
        #     print('col', col, kwargs.get(col))
        #     self.fields[col].value = kwargs.get(col) 

    def m2m_add(self, m2m_field_name, *args): # obj.add('classrooms', cl1, cl2, cl3)
        # if col in self.many_to_many:
        m2m_field = self.__class__.db.fields.get(m2m_field_name)

        if m2m_field.constraint != 'm2m':
            raise TypeError

        m2m_model = m2m_field.model
        through_model = m2m_field.through_model
        if isinstance(through_model, str):
            through_model = getattr(db.models, through_model)

        through_table_name = through_model.db.table_name

        reverse_field_1 = None 
        reverse_field_2 = None 
        for field_name, field in through_model.db.fields.items():
            if field.constraint == 'fkey' and field.model == self.__class__:
                reverse_field_1 = field_name
            elif field.constraint == 'fkey' and field.model == m2m_model:
                reverse_field_2 = field_name

        m2m_response = []
        for instance in args:
            kwargs = {
                f'{reverse_field_1}_id': self.id, 
                f'{reverse_field_2}_id': instance.id
            }

            # m2m_columns = ', '.join(kwargs.keys())

            # m2m_placeholders = ', '.join(['?'] * len(kwargs))
            # m2m_values = list(kwargs.values())
            # m2m_query = f"INSERT INTO {m2m_through_table_name} ({m2m_columns}) VALUES ({m2m_placeholders})" 

            m2m_response.append(through_model.db.create(**kwargs))

        setattr(self, m2m_field_name, m2m_response)

    def m2m_remove(self):
        # if not self.constraint == 'm2m':
        # raise AttributeError()

        pass 

    def m2m_clear(self, m2m_field_name):
        # if col in self.many_to_many:
        m2m_field = self.__class__.db.fields.get(m2m_field_name)

        if m2m_field.constraint != 'm2m':
            raise TypeError('Field is not a many_to_many field')

        m2m_model = m2m_field.model
        through_model = m2m_field.through_model
        if isinstance(through_model, str):
            through_model = getattr(db.models, through_model)

        through_table_name = through_model.db.table_name

        reverse_field_1 = None 
        for field_name, field in through_model.db.fields.items():
            if field.constraint == 'fkey' and field.model == self.__class__:
                reverse_field_1 = field_name
    
        through_model.db.delete(**{f'{reverse_field_1}_id': self.id})

class SessionManager:
    def __init__(self):
        self.current_user = None

    def login(self, user):
        self.current_user = user

    def logout(self):
        self.current_user = None

    def is_logged_in(self):
        return self.current_user is not None
