"""Communication

Elixys JSON communication for GUI
"""
import MySQLdb as SQL

class DBComm:
  def __init__(self):
    self.database = SQL.connect('localhost', 'root', 'kevin', 'elixys');
    pass
    
  def getFromDB(self, type, query):
    if (type=='sequence'):
      self.getSequence(query)
    elif (type=='unitop'):
      self.getUnitOperations(query)
    
  def getUnitOperations(self, query):
    print "tesT"
    rows = self.runQuery('SELECT * FROM unitoperations WHERE unitop_sequence=\'%s\'' % query)
  def getSequence(self, query):
    #sequence = self.runQuery('SHOW COLUMNS FROM sequences')
    sequence = self.runQuery('SELECT column_name FROM information_schema.columns WHERE table_name=\'sequences\'')
    print "\n\n"
    """
    for each in sequence:
      print each
    rows = self.runQuery('SELECT * FROM sequences WHERE id=\'%s\'' % query)
    for seq,row in map(None,sequence,rows):
      pass
      #print (seq,row)
     """ 
  def runQuery(self,query):
    try:

      cursor = self.database.cursor()
      cursor.execute(query)
      rows = cursor.fetchall()
      return rows
      for row in rows:
          print row
          for query in row:
            print query
      cursor.close()
    except SQL.Error, e:
        print "Error %d: %s" % (e.args[0],e.args[1])
        sys.exit(1)
        
  def closeDB(self):
    self.database = SQL.connect('localhost', 'root', 'kevin', 'elixys');

def test():
  sqldata = DBComm()
  #sqldata.runQuery('SELECT * FROM unitoperations ORDER BY unitop_step ASC')
  sqldata.getFromDB('sequence','1')
  sqldata.closeDB()
  
if __name__ == '__main__':
    test()