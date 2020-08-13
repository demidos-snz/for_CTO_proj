from datetime import date, datetime as dt

from peewee import Model, PrimaryKeyField, DateField, AutoField, CharField, ForeignKeyField, SqliteDatabase, fn

from settings import DB_NAME, MAX_COUNT_FAVOURITE_CITY

db = SqliteDatabase(DB_NAME)


def make_table_name(model_class: Model) -> str:
    table_name = ['_' + sym if sym.isupper() and i != 0 else sym
                  for i, sym in enumerate(model_class.__name__)]
    return ''.join(table_name).lower()


class BaseModel(Model):
    class Meta:
        database = db
        table_function = make_table_name

    def checking_exists_value_in_table(self, expression) -> bool:
        return self.select().where(expression).exists()

    @property
    def datetime_now(self) -> str:
        return dt.now().strftime('%Y-%m-%d %H:%M:%S')


class Users(BaseModel):
    user_id = PrimaryKeyField()
    date_registration = DateField()
    datetime_last_visit = DateField(formats='%Y-%m-%d %H:%M:%S')

    def insert_or_update_users_data(self, user_id: int):
        if self.checking_exists_value_in_table(expression=self._meta.columns['user_id'] == user_id):
            self.update_datetime_last_visit_user(user_id=user_id)
        else:
            self.insert(user_id=user_id, date_registration=date.today(),
                        datetime_last_visit=self.datetime_now).execute()

    def update_datetime_last_visit_user(self, user_id: int):
        self.update({'datetime_last_visit': self.datetime_now}) \
            .where(self._meta.columns['user_id'] == user_id).execute()


class Towns(BaseModel):
    town_id = AutoField()
    town_name = CharField(max_length=20)
    code_country = CharField(max_length=5)

    def insert_or_update_towns_data(self, town_name: str, country: str):
        if self.checking_exists_value_in_table(expression=(self._meta.columns['town_name'] == town_name) &
                                               (self._meta.columns['code_country'] == country)):
            pass
        #     todo update, where exists any country
        else:
            self.insert(town_name=town_name, code_country=country).execute()

    def get_all_favourite_towns(self, user_id: int) -> list:
        query = self.select(self._meta.columns['town_name']) \
            .join(UsersFavouriteTowns, on=UsersFavouriteTowns.town) \
            .where(UsersFavouriteTowns.user == user_id)
        return [row.town_name for row in query]

    def get_town_id(self, town_name: str) -> int:
        # fixme if town_name many
        query = self.select(self._meta.columns['town_id']) \
            .where(self._meta.columns['town_name'] == town_name)
        return [row for row in query][0]


class UsersFavouriteTowns(BaseModel):
    user = ForeignKeyField(model=Users, field=Users.user_id,
                           on_delete='CASCADE', backref='user')
    town = ForeignKeyField(model=Towns, field=Towns.town_id,
                           on_delete='CASCADE', backref='town')

    def delete_all_favourite_towns_from_user(self, user_id: int):
        self.delete().where(self._meta.columns['user_id'] == user_id).execute()

    def checking_favourite_town_name(self, user_id: int, town_id: int) -> (bool, None):
        if not self.town_favourite_name_exists(user_id=user_id, town_id=town_id):
            cnt_favourite_town = self.count_favourite_town_name_from_user_id(user_id=user_id)
            if cnt_favourite_town >= MAX_COUNT_FAVOURITE_CITY:
                return None
            self.add_users_favourite_towns_row(user_id=user_id, town_id=town_id)
            return True
        else:
            return False

    def town_favourite_name_exists(self, user_id: int, town_id: int) -> bool:
        return self.checking_exists_value_in_table(expression=(self._meta.columns['user_id'] == user_id) &
                                                              (self._meta.columns['town_id'] == town_id))

    def count_favourite_town_name_from_user_id(self, user_id: int) -> int:
        query = self.select(fn.COUNT().alias('count')).where(self._meta.columns['user_id'] == user_id)
        return [row.count for row in query][0]

    def add_users_favourite_towns_row(self, user_id: int, town_id: int):
        self.insert(user=user_id, town=town_id).execute()

    class Meta:
        primary_key = False


class QueryHistory(BaseModel):
    user = ForeignKeyField(model=Users, field=Users.user_id,
                           on_delete='CASCADE', backref='user')
    town = ForeignKeyField(model=Towns, field=Towns.town_id,
                           on_delete='CASCADE', backref='town')
    datetime_query = DateField(formats='%Y-%m-%d %H:%M:%S')

    def insert_query(self, towns_table: Towns, user_id: int, town_name: str):
        town_id = Towns.get_town_id(towns_table, town_name=town_name)
        self.insert(user_id=user_id, town_id=town_id,
                    datetime_query=self.datetime_now).execute()

    class Meta:
        primary_key = False
