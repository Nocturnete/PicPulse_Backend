from . import db

class BaseMixin():
    
    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
    
    def remove(self):
        db.session.remove(self)
        return True
    
    @classmethod
    def db_query(cls, *args):
        return db.session.query(cls, *args)
    
    @classmethod
    def get_filtered_by(cls, **kwargs):
        return cls.db_query().filter_by(**kwargs).one_or_none()