from . import db

class BaseMixin():
    
    @classmethod

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
    
    def remove(self):
        db.session.remove(self)
        return True