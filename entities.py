import peewee

db = peewee.SqliteDatabase("database.sqlite")


class BaseModel(peewee.Model):
    class Meta:
        database = db


class User(BaseModel):
    auth_token = peewee.TextField(verbose_name="Ключ авторизации")
    pkey = peewee.BlobField(verbose_name="Ключ шифрования")


class FileState(BaseModel):
    state = peewee.TextField(verbose_name="Название состояния", unique=True)
    r_accessible = peewee.BooleanField(verbose_name="Доступность для чтения", default=True)
    w_accessible = peewee.BooleanField(verbose_name="Доступность для записи", default=True)
    d_accessible = peewee.BooleanField(verbose_name="Доступность для удаления", default=True)


class File(BaseModel):
    name = peewee.TextField(verbose_name="Начальное имя", unique=False)
    uuid = peewee.UUIDField(verbose_name="Название в хранилище")
    state = peewee.ForeignKeyField(FileState, verbose_name="Cостояние файла")
    owner = peewee.ForeignKeyField(User, verbose_name="Владелец файла")
