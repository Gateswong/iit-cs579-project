from mongokit import Document, ObjectId, Connection

def get_connection(config):
    conn = Connection(
        host=config.MONGODB_IP,
        port=config.MONGODB_PORT
    )
    conn.register([Tweet, KeyWord])
    return conn

class Tweet(Document):
    __database__ = 'cs579proj'
    __collection__ = 'tweets'
    
    structure = {
        'keyword':str,
        'tweet':dict
    }
    
    required_fields = ['keyword', 'tweet']
    
class KeyWord(Document):
    __database__ = 'cs579proj'
    __collection__ = 'keywords'
    
    structure = {
        'team':str,
        'player':str,
        'salary':float,
        'city':str
    }
    
    required_fields = ['team', 'player', 'salary', 'city']

