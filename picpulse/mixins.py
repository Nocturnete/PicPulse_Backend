from . import db

class BaseMixin():

    @classmethod
    def create(cls, **kwargs):
        r = cls(**kwargs)
        return r.save()
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self.save()
    
    def save(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except:
            return False
        
    def delete(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except:
            return False
        
    @classmethod
    def db_query(cls, *args):
        return db.session.query(cls, *args)